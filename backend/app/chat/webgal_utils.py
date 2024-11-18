from flask import current_app, render_template
import random
from .bot_agent import BotAgent
import logging

logger = logging.getLogger('bot')


def text_to_webgal_scene(
    speaker: str,
    text: str,
    sess_id: str,
    model_path: str,
    expression_choices: dict[str, list[str]],
):
    """convert text returned by LLM to valid WebGAL scene
    called under context (because use of mood current_app)
    """
    sentence_buf = text_split_sentence(text)
    mood_buf = []
    for sent in sentence_buf:
        if "mood" in current_app.bot:
            mood_bot: BotAgent = current_app.bot["mood"]
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
        baseurl=f"http://127.0.0.1:{current_app.config['PORT']}/webgal/chat.txt",
    )

TEXT_SPLIT_PUNCTUATIONS = "。？！；\n"
def text_split_sentence(text:str):
    '''split a sentence (returned by LLM) into several sentences that fit WebGAL UI
    '''
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