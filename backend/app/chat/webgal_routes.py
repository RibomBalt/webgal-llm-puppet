from flask import (
    request,
    current_app,
    Response,
)
from uuid import UUID
from urllib.parse import unquote

from .bot_agent import ChatBot
from .webgal_utils import text_split_sentence, TEXT_SPLIT_PUNCTUATIONS, text_to_webgal_scene
from . import webgal


def load_bot(sess_id: str):
    """find botAgent object with sess_id in cache/db
    called under context
    """
    if sess_id in current_app.bot:
        # cache hit
        return current_app.bot.get(sess_id)
    else:
        # could raise IndexError
        bot = ChatBot.load_from_db(
            current_app.database.session,
            sess_id=UUID(sess_id),
            model_secret=current_app.config["MODEL_SECRETS"],
        )
        # so bot is not in cache, add to it
        current_app.app[bot.chat_session.id.hex] = bot
        return bot


@webgal.route("/newchat.txt")
def newchat():
    """create a new session"""
    # presets load
    bot_preset = current_app.config["MODEL_PRESETS"][
        current_app.config["DEFAULT_PRESET"]
    ]

    bot = None
    if "sess_id" in request.args:
        # sess_id provided, try to load from cache or database
        try:
            bot = load_bot(request.args.get("sess_id"))
        except IndexError:
            bot = None

    if bot is None:
        # create a new session
        bot = ChatBot.new_from_preset(bot_preset, current_app.config["MODEL_SECRETS"])

    sess_id = bot.chat_session.id.hex
    current_app.bot[sess_id] = bot

    script = text_to_webgal_scene(
        bot_preset["speaker"],
        bot_preset["welcome_message"],
        sess_id=sess_id,
        model_path=bot_preset["live2d_model_path"],
        expression_choices=bot_preset["mood"],
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
    try:
        bot = load_bot(sess_id=sess_id)
    except IndexError:
        current_app.logger.warning(f"chat session {sess_id} not found both in cache and db, start a new one")
        bot = ChatBot.new_from_preset(bot_preset, current_app.config["MODEL_SECRETS"])
        sess_id = bot.chat_session.id.hex
        current_app.bot[sess_id] = bot
    
    answer = bot.get_answer(prompt, stream=False)
    # TODO techniquely this is streamable, just send back a sentence at a time

    script = text_to_webgal_scene(
        bot_preset["speaker"],
        answer,
        sess_id=sess_id,
        model_path=bot_preset["live2d_model_path"],
        expression_choices=bot_preset["mood"],
    )

    return Response(script, mimetype="text/plain")


@webgal.route("/save")
def save():
    """save all current bots to database"""
    try:
        for bot in current_app.bot.values():
            bot.save_to_db(current_app.database.session, commit=False)
    finally:
        current_app.database.session.commit()

    return {"result": "ok"}
