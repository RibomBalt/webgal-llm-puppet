from flask import (
    request,
    current_app,
    Response,
)
from uuid import UUID
from urllib.parse import unquote
from queue import Queue, Empty
from .bot_agent import ChatBot
from ..typt_hint import Preset
from .webgal_utils import (
    text_split_sentence,
    TEXT_SPLIT_PUNCTUATIONS,
    sentence_mood_to_webgal_scene,
)
from flask_apscheduler.scheduler import BackgroundScheduler
from . import webgal
import logging


def load_bot(sess_id: str, bot_preset: Preset):
    """find ChatBot object with sess_id in cache/db
    called under context
    """
    if sess_id in current_app.bot:
        # cache hit
        return current_app.bot.get(sess_id)
    else:
        # could raise IndexError
        try:
            bot = ChatBot.load_from_db(
                current_app.database.session,
                sess_id=UUID(sess_id),
                model_secret=current_app.config["MODEL_SECRETS"],
            )
        except IndexError:
            # so not in cache and db, create it
            current_app.logger.warning(
                f"chat session {sess_id} not found both in cache and db, start a new one"
            )
            bot = ChatBot.new_from_preset(
                bot_preset, current_app.config["MODEL_SECRETS"]
            )

        # so bot is not in cache, add to it with a message queue
        msg_queue = Queue()
        current_app.bot[bot.chat_session.id.hex] = (bot, msg_queue)
        return (bot, msg_queue)


def task_put_sentence_into_queue(
    resp_queue: Queue,
    resp_gen,
    mood_bot: ChatBot | None = None,
    proxy_url: str | None = None,
):
    """
    this is called by apscheduler, and
    """
    logger = logging.getLogger("bot")

    word_buf = ""
    for ichunk, chunk in enumerate(resp_gen):
        if chunk is not None:
            word_buf += chunk
            # NOTE chunk can be empty string
            if chunk and (chunk in TEXT_SPLIT_PUNCTUATIONS):
                # the word_buf must be splittable now
                sentences = text_split_sentence(word_buf)
                for sent in sentences[:-1]:
                    # each sent is a complete sentence
                    # here we block the mood analyzer (since this is threaded background)
                    if mood_bot is not None:
                        mood = mood_bot.get_answer(
                            sent, stream=False, proxy_url=proxy_url
                        )
                    else:
                        mood = ""
                    logger.debug(f"mood analyze: {sent}|{mood}|")
                    resp_queue.put((sent, mood))

                logger.debug(f"text_line_breaker: {sentences}|{word_buf}|")
                # last sentence might not be incomplete
                word_buf = sentences[-1]
        else:
            # if there
            if word_buf:
                if mood_bot is not None:
                    mood = mood_bot.get_answer(
                        word_buf, stream=False, proxy_url=proxy_url
                    )
                else:
                    mood = ""
                resp_queue.put((word_buf, mood))

                logger.debug(f"text_line_breaker at end: {word_buf}|<end>|")
            break

    resp_queue.put((None, None))
    logger.info("mood analyzer complete")
    return True


def task_get_sentence_from_queue(msg_queue: Queue, at_least=1):
    """get items from msg_queue
    get `at_least` number blocking, try reading rest non-blocking
    """
    sent_buf = []
    mood_buf = []
    for _ in range(at_least):
        sent, mood = msg_queue.get()
        sent_buf.append(sent)
        mood_buf.append(mood)

    # also get all non-empty
    try:
        while not msg_queue.empty():
            sent, mood = msg_queue.get(False)
            sent_buf.append(sent)
            mood_buf.append(mood)

    except Empty:
        pass

    return sent_buf, mood_buf


@webgal.route("/newchat.txt")
def newchat():
    """create a new session"""
    # presets load
    bot_preset = current_app.config["MODEL_PRESETS"][
        current_app.config["DEFAULT_PRESET"]
    ]

    if "sess_id" in request.args:
        # sess_id provided, try to load from cache or database
        bot, msg_queue = load_bot(request.args.get("sess_id"), bot_preset)
        sess_id = bot.chat_session.id.hex

    else:
        # create a new session
        bot = ChatBot.new_from_preset(bot_preset, current_app.config["MODEL_SECRETS"])
        msg_queue = Queue()

        sess_id = bot.chat_session.id.hex
        current_app.bot[sess_id] = (bot, msg_queue)

    # for a new queue, extract all existing
    # TODO assume no race condition with e.g. two connections from WebGAL frontend
    while not msg_queue.empty():
        msg_queue.get()

    script = sentence_mood_to_webgal_scene(
        [bot_preset["welcome_message"]],
        ["高兴"],
        sess_id,
        baseurl=f"{current_app.config['WEBGAL_BACKEND_BASEURL']}/webgal/chat.txt",
        speaker_preset=bot_preset,
        include_input=True,
    )

    return Response(script, mimetype="text/plain")


@webgal.route("/chat.txt")
def getchat():
    """ """
    sess_id, prompt = request.query_string.decode().split(":", maxsplit=1)
    bot_preset = current_app.config["MODEL_PRESETS"][
        current_app.config["DEFAULT_PRESET"]
    ]

    prompt = unquote(prompt)

    mode = "new_input"
    if prompt.startswith("__cmd__next"):
        # command mode
        mode = "next"
    elif prompt.startswith("再见"):
        mode = "exit"

    bot, msg_queue = load_bot(sess_id=sess_id, bot_preset=bot_preset)

    if mode == "exit":
        # if exit, first clear the queue
        while not msg_queue.empty():
            msg_queue.get()
        #
        script = sentence_mood_to_webgal_scene(
            [],
            [],
            sess_id=sess_id,
            baseurl=f"{current_app.config['WEBGAL_BACKEND_BASEURL']}/webgal/chat.txt",
            speaker_preset=bot_preset,
            include_exit=True,
        )

    else:
        if mode == "new_input":
            # with new input, first clear the queue
            while not msg_queue.empty():
                msg_queue.get()

            # request a new answer streamable
            answer_gen = bot.get_answer(
                prompt,
                stream=True,
                sse=False,
                proxy_url=current_app.config["PROXY_URL"],
            )
            scheduler: BackgroundScheduler = current_app.scheduler

            # add background task
            # TODO is it possible? out of context?
            mood_bot = current_app.bot.get("mood", None)
            proxy_url = current_app.config["PROXY_URL"]
            scheduler.add_job(
                lambda: task_put_sentence_into_queue(
                    msg_queue,
                    answer_gen,
                    mood_bot=mood_bot,
                    proxy_url=proxy_url,
                )
            )

        # whether new_input or next, at least get one message
        # there must be one, might be a None
        sent_buf, mood_buf = task_get_sentence_from_queue(msg_queue)
        # check if there is None is sent_buf, marking the end of answering
        if sent_buf[-1] is None:
            sent_buf = sent_buf[:-1]
            mood_buf = mood_buf[:-1]
            include_input = True
        else:
            include_input = False

        current_app.logger.debug(
            f"chunks: {mode}, {sent_buf}, {mood_buf}, {include_input}"
        )

        script = sentence_mood_to_webgal_scene(
            sent_buf,
            mood_buf,
            sess_id=sess_id,
            baseurl=f"{current_app.config['WEBGAL_BACKEND_BASEURL']}/webgal/chat.txt",
            speaker_preset=bot_preset,
            include_input=include_input,
        )

    current_app.logger.debug(f"generate scripts: \n{script}")
    return Response(script, mimetype="text/plain")


@webgal.route("/save")
def save():
    """save all current bots to database"""
    try:
        for bot in current_app.bot.values():
            if isinstance(bot, tuple):
                bot = bot[0]

            bot.save_to_db(current_app.database.session, commit=False)
    finally:
        current_app.database.session.commit()

    return {"result": "ok"}
