from pydantic import BaseModel, constr, Field, ConfigDict
from fastapi import Depends
from openai import AsyncOpenAI
import httpx
from .bot import BotParams, BotPreset, BotSecret
from ..config import AppSettings, get_settings
from ..logger import model_logger
from uuid import UUID, uuid4
from datetime import datetime
from enum import Enum
import random
from aiocache import RedisCache, SimpleMemoryCache


class ChatRole(str, Enum):
    system = "system"
    user = "user"
    assistant = "assistant"


class ChatMessage(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    role: ChatRole
    msg: str
    session: UUID
    mood: str = ""
    others: str = ""
    time: datetime = Field(default_factory=datetime.now)

    model_config = ConfigDict(from_attributes=True)

    def export_message(self):
        return {"role": self.role, "content": self.msg}


class ChatSessionMeta(BaseModel):
    """only contains non expanding informations"""

    id: UUID = Field(default_factory=uuid4)
    name: str = Field(default_factory=random.randbytes(8).hex)
    llm_name: str = "mockai"
    system_prompt: str = ""
    llm_params: BotParams = BotParams()
    max_memory: int = 30
    current_msg_length: int = 0

    model_config = ConfigDict(from_attributes=True)

    def export_system_prompt(self):
        return (
            {"role": ChatRole.system, "content": self.system_prompt}
            if self.system_prompt
            else None
        )


class ChatSession(BaseModel):
    """
    llm_name: the name to access certain LLM, not api_key, not internal name
    """

    meta: ChatSessionMeta = ChatSessionMeta()
    # we keep this messages ordered by time
    messages: list[ChatMessage] = []
    non_cached: int = 0

    model_config = ConfigDict(from_attributes=True)

    @property
    def last_chat_time(self) -> datetime:
        if self.messages:
            self.messages[-1].time

        else:
            # minimum possible value of datetime
            return datetime.min

    def add_message(
        self, role: ChatRole, message: str, mood: str = "", others: str = ""
    ):
        new_msg = ChatMessage(
            role=role, msg=message, session=self.meta.id, mood=mood, others=others
        )
        self.messages.append(new_msg)
        self.meta.current_msg_length += 1
        self.non_cached += 1

    @classmethod
    def from_preset(cls, preset: BotPreset, max_memory: int = 30):
        """create from preset"""

        meta = ChatSessionMeta(
            name=f"{preset.speaker}.{preset.llm_name}.{random.randbytes(4).hex()}",
            llm_name=preset.llm_name,
            system_prompt=preset.system_prompt,
            llm_params=preset.llm_params,
            max_memory=max_memory,
            current_msg_length=0,
        )

        new_sess = cls(meta=meta, messages=[])
        if preset.welcome_message:
            new_sess.add_message(ChatRole.assistant, preset.welcome_message)

        return new_sess

    @classmethod
    async def load_from_redis_cache(
        cls, sess_id: UUID, cache: RedisCache | SimpleMemoryCache
    ):
        # check exists
        if isinstance(sess_id, str):
            sess_id = UUID(sess_id)

        sess_cache_key = f"session:{sess_id.hex}"
        if not await cache.exists(sess_cache_key):
            model_logger.warning(f"try reading {sess_cache_key} from cache, not found")
            raise IndexError(f"{sess_id.hex} not found in cache")

        sess_meta = ChatSessionMeta.model_validate_json(
            await cache.get(sess_cache_key)
        )

        history_keys = [
            f"history:{sess_id.hex}:{msg_id}"
            for msg_id in range(
                max(0, sess_meta.current_msg_length - sess_meta.max_memory),
                sess_meta.current_msg_length,
            )
        ]
        sess_his = (
            [
                ChatMessage.model_validate_json(d)
                for d in (await cache.multi_get(history_keys))
            ]
            if history_keys
            else []
        )

        return ChatSession(meta=sess_meta, messages=sess_his)

    async def save_to_redis_cache(self, cache: RedisCache | SimpleMemoryCache):
        sess_id = self.meta.id

        sess_cache_key = f"session:{sess_id.hex}"
        await cache.set(sess_cache_key, self.meta.model_dump_json())
        model_logger.debug(f"save to cache: {sess_cache_key}")

        msg_to_cache = [
            (
                f"history:{sess_id.hex}:{self.meta.current_msg_length + imsg}",
                self.messages[imsg].model_dump_json(),
            )
            for imsg in range(-self.non_cached, 0)
        ]
        await cache.multi_set(msg_to_cache)
        model_logger.debug(f"save to cache: {[pair[0] for pair in msg_to_cache]}")
        self.non_cached = 0

        return True

    async def get_answer_a(
        self, settings: AppSettings, prompt: str = "", preset_name: str = "sakiko"
    ):
        """
        async gen that return pieces of answers
        """
        self.add_message("user", prompt)

        secret = settings.secret_pool.get(settings.bot_preset.get(preset_name).llm_name)
        client = AsyncOpenAI(
            api_key=secret.api_key,
            base_url=secret.base_url,
            http_client=httpx.AsyncClient(proxy=settings.proxy_url)
            if settings.proxy_url
            else None,
        )

        # construct messages
        message_request = (
            [self.meta.export_system_prompt()] if self.meta.system_prompt else []
        )
        history = []
        for _, msg in zip(range(self.meta.max_memory), self.messages[::-1]):
            # we use role=='clear' message to represent clear
            # currently not implemented
            if msg.role == "clear":
                break

            history.append(msg.export_message())

        message_request.extend(history[::-1])

        stream = await client.chat.completions.create(
            model=secret.model,
            messages=message_request,
            stream=True,
            **self.meta.llm_params.model_dump(mode="json"),
        )

        async def resp_gen():
            resp = []
            async for chunk in stream:
                chunk_piece = chunk.choices[0].delta.content or ""
                yield chunk_piece
                resp.append(chunk_piece)

            resp_text = "".join(resp)
            self.add_message("assistant", resp_text)

            yield None

        return resp_gen()
