from flask import current_app, render_template
import random
from .bot_agent import ChatBot
from ..typt_hint import Preset
import logging

logger = logging.getLogger("bot")


def sentence_mood_to_webgal_scene(
    sent_buf: list[str],
    mood_buf: list[str],
    sess_id: str,
    baseurl: str,
    speaker_preset: Preset,
    include_input=False,
    include_exit=False,
):
    """
    include_input: if set, include `getUserInput` at the end. Next request would be a new chat message
    include_exit: if set, include `end`. sent_buf and moodd_buf would be ignored
    """
    speaker = speaker_preset["speaker"]
    model_path = speaker_preset["live2d_model_path"]
    expression_choices = speaker_preset["mood"]

    # parse flags
    listening_mood = random.choice(expression_choices["listening"]).split(":")

    if include_exit:
        # TODO preserve previous mood?
        sent_buf.append(speaker_preset["bye_message"])
        mood_buf.append("高兴")

    # mood str -> motion+expression set
    mood_cmd_buf = []
    expression_keys = list(expression_choices.keys())
    for mood in mood_buf:
        if mood not in expression_choices:
            mood = random.choice(expression_keys)
            logger.debug(f"choose random mood:|{mood}|")

        mood_cmd_buf.append(random.choice(expression_choices[mood]).split(":"))

    scene = render_template(
        "chat.txt",
        sess_id=sess_id,
        speaker=speaker,
        sentences_expressions=zip(sent_buf, mood_cmd_buf),
        model_figure=model_path,
        listening=listening_mood,
        include_input=include_input,
        include_exit=include_exit,
        baseurl=baseurl,
    )

    return scene


def text_to_webgal_scene(
    speaker: str,
    text: str,
    sess_id: str,
    model_path: str,
    expression_choices: dict[str, list[str]],
    include_input=True,
    include_exit=False,
):
    """convert text returned by LLM to valid WebGAL scene
    called under context (because use of mood current_app)
    """
    sentence_buf = text_split_sentence(text)
    mood_buf = []
    for sent in sentence_buf:
        if "mood" in current_app.bot:
            mood_bot: ChatBot = current_app.bot["mood"]
            mood_answer = mood_bot.get_answer(sent, stream=False).strip()
            logger.debug(f"mood for {sent}:|{mood_answer}|")
            if mood_answer not in expression_choices.keys():
                mood_answer = None
        else:
            mood_answer = None

        if mood_answer is None:
            mood_answer = random.choice(expression_choices.keys())
            logger.debug(f"choose random mood:|{mood_answer}|")

        # now use happy emotion for all cases
        listening_mood = random.choice(expression_choices["listening"]).split(":")
        mood_buf.append(random.choice(expression_choices[mood_answer]).split(":"))

    return render_template(
        "chat.txt",
        sess_id=sess_id,
        speaker=speaker,
        sentences_expressions=zip(sentence_buf, mood_buf),
        model_figure=model_path,
        listening=listening_mood,
        include_input=include_input,
        include_exit=include_exit,
        baseurl=f"http://127.0.0.1:{current_app.config['PORT']}/webgal/chat.txt",
    )


TEXT_SPLIT_PUNCTUATIONS = "。？！；\n"


def text_split_sentence(text: str):
    """split a sentence (returned by LLM) into several sentences that fit WebGAL UI"""
    # split text
    # remove double newline
    text = text.replace("\n\n", "\n")
    # split by 。or \n
    sentence_buf = []
    c_marker = 0
    for i_c, c in enumerate(text):
        # better split sentence
        if c in TEXT_SPLIT_PUNCTUATIONS:
            # discard consecutive punctuations
            if i_c > c_marker:
                sentence_buf.append(text[c_marker : i_c + 1].strip())
                c_marker = i_c + 1
    if c_marker < len(text) - 1:
        sentence_buf.append(text[c_marker:].strip())

    return sentence_buf
