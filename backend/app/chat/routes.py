from flask import (
    request,
    render_template,
    current_app,
    stream_with_context,
    Response,
)
from uuid import UUID
import json
import random

from .orm import ChatSession
from .bot_agent import BotAgent
from . import chat as chat_bp


def session_id_to_bot(sess_key="session_id") -> BotAgent:
    """
    called under context
    raise IndexError when invalid session, contain a Response object
    """
    chat_session_id = request.json.get(sess_key, "")
    if not chat_session_id:
        raise IndexError({"result": "error", "reason": "no chat_session id"})

    try:
        bot: BotAgent = BotAgent.load_from_db(
            db_session=current_app.database.session,
            sess_id=UUID(chat_session_id),
            model_secret=current_app.config["MODEL_SECRETS"],
        )

    except (IndexError, ValueError) as err:
        raise IndexError(
            {
                "result": "error",
                "reason": f"Error loading ChatSession from db: {err.args[0]}",
            }
        )

    return bot


@chat_bp.route("/")
def index():
    return render_template("index.html")


#  ======== APIs =========
@chat_bp.route("/chat_sessions", methods=["GET"])
def list_sessions():
    db = current_app.database
    sess_ids = {
        u.hex: {"time": t.timestamp()}
        for u, t in ChatSession.list_session_ids(db.session)
    }

    return sess_ids


@chat_bp.route("/chat_sessions", methods=["PUT"])
def new_session():
    secret_key = request.json.get("secret_key", "mockai")
    system_prompt = request.json.get("system_prompt", "")
    model_params = request.json.get("model_params", {})
    max_memory = request.json.get("max_memory", BotAgent.MAX_MEMORY_DEFAULT)

    secret = current_app.config["MODEL_SECRETS"][secret_key]

    bot = BotAgent.new_session(
        f"{secret_key}.{random.randint(10000,99999)}",
        secret_key=secret_key,
        system_prompt=system_prompt,
        model_params=json.dumps(model_params),
        model_secret=secret,
        max_memory=max_memory,
        init_history=None,
        unsaved_msg=0,
    )

    bot.save_to_db(current_app.database.session)

    return {"result": "ok", "session_id": bot.chat_session.id.hex}


@chat_bp.route("/chat_sessions", methods=["POST"])
def edit_session():
    """ """
    try:
        bot = session_id_to_bot()
    except IndexError as err:
        return Response(
            json.dumps(err.args[0]), status=404, mimetype="application/json"
        )

    edit_properties = request.json.get("edit", {})
    for k, v in edit_properties.items():
        # sanitize keys
        if k in (
            "name",
            "secret_key",
            "system_prompt",
        ):
            # TODO sanitize values as well
            setattr(bot.chat_session, k, str(v))
        elif k in ("model_params",):
            setattr(bot.chat_session, k, json.dumps(v))
        elif k in ("max_memory",):
            setattr(bot.chat_session, k, int(v))

    return {"result": "ok", "session": bot.chat_session.to_dict()}


@chat_bp.route("/chat", methods=["POST"])
def chat_completion():
    # TODO add options to temporarily change model params?
    try:
        bot = session_id_to_bot()
    except IndexError as err:
        return Response(
            json.dumps(err.args[0]), status=404, mimetype="application/json"
        )

    user_prompt = request.json.get("user_prompt", "continue")
    do_sse = int(request.args.get("do_sse", True))

    # TODO maybe update session_name if this is the first conversation

    # stream with SSE
    # NOTE: the generator should run until last return...
    if do_sse:
        msg_gen = bot.get_answer(user_prompt, stream=True)
        resp = Response(stream_with_context(msg_gen), mimetype="text/event-stream")

        return resp
    else:
        msg_ret = bot.get_answer(user_prompt, stream=False)
        return msg_ret


#  =================


@chat_bp.after_request
def after_request(resp):
    return resp
