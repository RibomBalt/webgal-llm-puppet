from flask import (
    request,
    session,
    render_template,
    send_from_directory,
    current_app,
    stream_with_context,
    Response,
)
from uuid import UUID
import json
import random
from datetime import datetime
from urllib.parse import unquote

from .orm import ChatSession
from .bot_agent import BotAgent
from . import webgal


def text_to_webgal_scene(speaker: str, text: str, sess_id: str, model_path:str, expression_choices:dict[str,list[str]]):
    """ """
    # split text
    # remove double newline
    text = text.replace("\n\n", "\n")
    # split by 。or \n
    sentence_buf = []
    c_marker = 0
    for i_c, c in enumerate(text):
        # better split sentence
        if c in "。？！\n":
            # discard consecutive punctuations
            if i_c > c_marker:
                sentence_buf.append(text[c_marker : i_c + 1].strip())
                c_marker = i_c + 1
    if c_marker < len(text) - 1:
        sentence_buf.append(text[c_marker:].strip())

    # TODO also get mood for each sentence
    # now use random
    
    listening_mood = random.choice(expression_choices['listening']).split(':')
    expression_mood = [random.choice(expression_choices['开心']).split(':') for _ in sentence_buf]

    return render_template(
        "chat.txt",
        sess_id=sess_id,
        speaker=speaker,
        sentences_expressions=zip(sentence_buf, expression_mood),
        model_figure=model_path,
        listening=listening_mood,
        baseurl=f"http://127.0.0.1:{current_app.config['PORT']}/webgal/chat.txt",
    )


@webgal.route("/newchat.txt")
def newchat():
    """create a new session"""
    # start new session
    bot_preset = current_app.config["MODEL_PRESETS"][
        current_app.config["DEFAULT_PRESET"]
    ]
    bot = BotAgent.new_session(
        f"sakiko-{random.randint(10000,99999)}",
        secret_key=bot_preset["model"],
        system_prompt=bot_preset["system_prompt"],
        model_secret=current_app.config["MODEL_SECRETS"][bot_preset["model"]],
        model_params=json.dumps(bot_preset["model_params"]),
    )

    welcome_message = bot_preset["welcome_message"]
    bot.new_message("assistant", welcome_message)
    sess_id = bot.chat_session.id.hex

    # TODO hardcode name
    script = text_to_webgal_scene(bot_preset["speaker"], welcome_message, sess_id=sess_id, model_path=bot_preset["live2d_model_path"], expression_choices=bot_preset["mood"])

    bot.save_to_db(current_app.database.session)

    return Response(script, mimetype="text/plain")


@webgal.route("/chat.txt")
def getchat():
    """ """
    sess_id, prompt = request.query_string.decode().split(":", maxsplit=1)
    bot_preset = current_app.config["MODEL_PRESETS"][
        current_app.config["DEFAULT_PRESET"]
    ]

    prompt = unquote(prompt)
    bot = BotAgent.load_from_db(
        current_app.database.session,
        sess_id=UUID(sess_id),
        model_secret=current_app.config["MODEL_SECRETS"],
    )
    answer = bot.get_answer(prompt, stream=False)
    
    script = text_to_webgal_scene(bot_preset["speaker"], answer, sess_id=sess_id, model_path=bot_preset["live2d_model_path"], expression_choices=bot_preset["mood"])

    bot.save_to_db(current_app.database.session)

    return Response(script, mimetype="text/plain")
