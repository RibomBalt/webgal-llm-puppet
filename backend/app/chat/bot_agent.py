from openai import OpenAI
from .orm import ChatSession, ChatMessage
from uuid import UUID
from flask_sqlalchemy.session import Session
from sqlalchemy import select
import json
import random
import logging
from datetime import datetime
from ..typt_hint import Secret, Preset

logger = logging.getLogger("bot")


class ChatBot:
    """All interaction with Bots
    The chat history view only includes messages from last clear
    """

    MAX_MEMORY_DEFAULT = 30

    def __init__(
        self,
        init_session: ChatSession,
        model_secret: Secret = None,
        init_history: list[ChatMessage] = None,
        unsaved_msg: int = 0,
    ) -> None:
        """
        Only params that are not stored in ChatSession/ChatMessage should be accepted here
        init_session (mandatory):
            for a brand new session, use `new`

        model_secret: the corresponding secret object
            In the session, secret is not stored, so the key to the secret should be stored
        db_session: if not None, initialize ORM with db_session
        max_memory: maximum entries of chat history to send back to AI
        """
        # extract model secrets
        if model_secret is None:
            # default value for model secret
            model_secret = {
                "model": "mockai",
                "api_key": "sk-",
                "base_url": "http://localhost:5002/v1",
            }

        self.model_secret = model_secret
        self.chat_session = init_session
        self.chat_history = [] if init_history is None else init_history
        self.unsaved_msg = min(unsaved_msg, len(self.chat_history))

    @classmethod
    def new_session(
        cls,
        session_name: str = None,
        secret_key: str = "mockai",
        system_prompt: str = "",
        model_params: str = "{}",
        model_secret: Secret = None,
        max_memory=MAX_MEMORY_DEFAULT,
        init_history: list[ChatMessage] = None,
        unsaved_msg: int = 0,
    ):
        """create a brand new session"""
        if session_name is None:
            session_name = f"{secret_key}.{random.randint(10000, 99999)}"

        init_session = ChatSession.create(
            name=session_name,
            secret_key=secret_key,
            system_prompt=system_prompt,
            model_params=model_params,
            max_memory=max_memory,
        )

        obj = cls(
            init_session=init_session,
            model_secret=model_secret,
            init_history=init_history,
            unsaved_msg=unsaved_msg,
        )
        return obj

    def new_message(self, role, msg, mood="", others="{}", append=True):
        """create a new message for this session"""
        next_message = ChatMessage.create(
            role=role, msg=msg, session=self.chat_session.id, mood=mood, others=others
        )

        if append:
            self.chat_history.append(next_message)
            self.unsaved_msg += 1
            self.chat_session.last_chat_time = next_message.time

        return next_message

    @classmethod
    def new_from_preset(cls, bot_preset: Preset, secret_keybed: dict[str, Secret]):
        """A caller-friendly interface to create a new bot.
        all required field in presets: speaker, model, system_prompt, model, model_params, welcome_message
        """
        bot = cls.new_session(
            f"{bot_preset['speaker']}-{bot_preset['model']}-{random.randint(10000,99999)}",
            secret_key=bot_preset["model"],
            system_prompt=bot_preset["system_prompt"],
            model_secret=secret_keybed[bot_preset["model"]],
            model_params=json.dumps(bot_preset["model_params"]),
        )

        if bot_preset["welcome_message"]:
            bot.new_message("assistant", bot_preset["welcome_message"])

        return bot

    @classmethod
    def load_from_db(
        cls,
        db_session: Session,
        sess_id: UUID,
        model_secret: Secret,
    ):
        """
        load session from ORM and construct a ChatBot

        raise IndexError if no session with this id is found

        TODO should there be a function to only load ChatSession object?

        sess_id: UUID
        model_secret: secret dict, or map of secret dict
        """
        # load sess could raise NoResultFound

        init_session = ChatSession.load_from_db_by_id(db_session, sess_id)
        if init_session is None:
            raise IndexError(f"no session id='{sess_id}'")

        # load atmost `max_history` newest messages of this session
        init_history = (
            db_session.execute(
                select(ChatMessage)
                .filter_by(session_id=sess_id)
                .order_by(ChatMessage.time.desc())
                .limit(init_session.max_memory)
            )
            .scalars()
            .all()
        )[::-1]

        # sometimes we pass the model_secret is a dict for real model secrets, and the secret_key is stored in ChatSession object
        if "api_key" not in model_secret.keys():
            if init_session.secret_key in model_secret.keys():
                model_secret = model_secret[init_session.secret_key]
            else:
                raise ValueError(f"invalid model_secret: {model_secret}")

        bot = ChatBot(
            init_history=init_history,
            init_session=init_session,
            model_secret=model_secret,
            unsaved_msg=0,
        )

        return bot

    def save_to_db(self, db_session: Session, commit=True):
        """
        save ChatSession, new ChatMessages to database, commit, and reset unsaved_counter to 0

        this function should be called under context
        """
        # save session
        if (
            orig_sess := ChatSession.load_from_db_by_id(
                db_session, self.chat_session.id
            )
        ) is not None:
            for k in self.chat_session.to_dict():
                setattr(orig_sess, k, getattr(self.chat_session, k))

        else:
            db_session.add(self.chat_session)

        # add chat history
        for i_msg in range(self.unsaved_msg, 0, -1):
            db_session.add(self.chat_history[-i_msg])

        # commit and reset unsaved counter
        if commit:
            db_session.commit()

        # TODO if we add redis cache in the future, there should be a separate counter for messages added but not commited
        # this counter only affect where to start adding messages
        self.unsaved_msg = 0

    def load_chat_history(
        self,
        db_session: Session,
        time_before: datetime = None,
        modify_this_object=False,
        max_read_items: int = MAX_MEMORY_DEFAULT,
    ):
        """load more history from database
        modify_this_object: if True, ignore time_before, and
        """
        if time_before is None:
            time_before = datetime.max

        if modify_this_object and len(self.chat_history) > 0:
            # get messages earlier than the first message here
            time_before = self.chat_history[0].time

        new_history = (
            db_session.execute(
                select(ChatMessage)
                .filter_by(session_id=self.chat_session.id)
                .where(ChatMessage.time < time_before)
                .order_by(ChatMessage.time.desc())
                .limit(max_read_items)
            )
            .scalars()
            .all()
        )[::-1]

        # make it time sequenced
        if modify_this_object:
            self.chat_history = new_history + self.chat_history

        return new_history

    def get_answer(
        self,
        new_chat: str,
        stream=True,
        extract_chunk=True,
        db_session=None,
    ):
        """get answer by interact with bot
        answer would append to history after stream queue is drained (stream=True) or immediately (stream=False)

        db_session: if set, save_to_db at the end of stream of SSE
        NOTE: if extract_chunk is False, won't update self.chat_history
        """
        self.new_message("user", new_chat)

        # extract system prompt
        system_prompt = self.chat_session.export_system_prompt()
        message_request = [system_prompt] if system_prompt is not None else []

        # extract recent max_memory of history or until a clear event
        history = []
        for _, msg in zip(range(self.chat_session.max_memory), self.chat_history[::-1]):
            # we use role=='clear' message to represent clear
            if msg.role == "clear":
                break

            history.append(msg.export_message())

        message_request.extend(history[::-1])

        # model params
        model_params = json.loads(self.chat_session.model_params)

        logger.debug(f"{message_request}, {model_params}")
        client = OpenAI(
            api_key=self.model_secret["api_key"], base_url=self.model_secret["base_url"]
        )
        resp = client.chat.completions.create(
            model=self.model_secret["model"],
            messages=message_request,
            stream=stream,
            **model_params,
        )

        if extract_chunk:
            if stream:
                # directly a generator. end with a None element
                def chunk_stream():
                    resp_content = []
                    for ichunk, chunk in enumerate(resp):
                        content = chunk.choices[0].delta.content
                        if content is None:
                            # there could be a None at end, could be not
                            break
                        else:
                            resp_content.append(content)

                        # the None is not stripped to notify EOF downstream
                        yield (
                            "data: "
                            + json.dumps(
                                {"delta": content, "index": ichunk, "type": "delta"}
                            )
                            + "\n\n"
                        )

                    # EOF
                    self.new_message("assistant", "".join(resp_content))
                    # make sure to save this to db before really breakup
                    if db_session is not None:
                        self.save_to_db(db_session=db_session)
                    # there should be a notice of EOF to the server
                    # we put it after DB to prevent Race condition, though it might be slower (maybe irrelavent)
                    yield "data: " + json.dumps({"type": "EOF"}) + "\n\n"

                return chunk_stream()

            else:
                # TODO check, error handling
                resp_content = resp.choices[0].message.content
                self.new_message("assistant", resp_content)
                if db_session is not None:
                    self.save_to_db(db_session=db_session)

                return resp_content

        else:
            return resp

    def to_dict(self):
        obj = {}
        obj["model_secret"] = self.model_secret
        obj["chat_session"] = self.chat_session.to_dict()
        obj["chat_history"] = []
        for msg in self.chat_history:
            obj["chat_history"].append(msg.to_dict())
        obj["unsaved_msg"] = self.unsaved_msg

        return obj

    @classmethod
    def from_dict(cls, kv: dict):
        chat_history = [ChatMessage.from_dict(d) for d in kv["chat_history"]]
        chat_session = ChatSession.from_dict(kv["chat_session"])
        obj = cls(
            init_session=chat_session,
            model_secret=kv["model_secret"],
            init_history=chat_history,
            unsaved_msg=kv["unsaved_msg"],
        )

        return obj

    __setstate__ = from_dict
    __getstate__ = to_dict

    def __str__(self):
        return f"{self.__class__.__name__}({json.dumps(self.to_dict())})"
