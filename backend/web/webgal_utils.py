import logging
import re

logger = logging.getLogger("bot")


# def sentence_mood_to_webgal_scene(
#     sent_buf: list[str],
#     mood_buf: list[str],
#     sess_id: str,
#     baseurl: str,
#     speaker_preset: BotPreset,
#     include_input=False,
#     include_exit=False,
# ):
#     """
#     include_input: if set, include `getUserInput` at the end. Next request would be a new chat message
#     include_exit: if set, include `end`. sent_buf and moodd_buf would be ignored
#     """
#     speaker = speaker_preset["speaker"]
#     model_path = speaker_preset["live2d_model_path"]
#     expression_choices = speaker_preset["mood"]

#     # parse flags
#     listening_mood = random.choice(expression_choices["listening"]).split(":")

#     if include_exit:
#         # TODO preserve previous mood?
#         sent_buf.append(speaker_preset["bye_message"])
#         mood_buf.append("高兴")

#     # mood str -> motion+expression set
#     mood_cmd_buf = []
#     expression_keys = list(expression_choices.keys())
#     for mood in mood_buf:
#         if mood not in expression_choices:
#             mood = random.choice(expression_keys)
#             logger.debug(f"choose random mood:|{mood}|")

#         mood_cmd_buf.append(random.choice(expression_choices[mood]).split(":"))

#     scene = render_template(
#         "chat.txt",
#         sess_id=sess_id,
#         speaker=speaker,
#         sentences_expressions=zip(sent_buf, mood_cmd_buf),
#         model_figure=model_path,
#         listening=listening_mood,
#         include_input=include_input,
#         include_exit=include_exit,
#         baseurl=baseurl,
#     )

#     return scene



TEXT_SPLIT_PUNCTUATIONS = "。？！；\n"

# match a sentence 
match_first_sentence = re.compile(r'^((（[^）]+?）)|^([(][^)]+?[)])|(([^。？！（；\n]*?[。？！；\n]+)))')
match_parathesis = re.compile(r'（[^）]+?）')
match_parathesis_ascii = re.compile(r'[(][^)]+?[)]')

def text_split_sentence(text: str):
    """split a sentence (returned by LLM) into several sentences that fit WebGAL UI
    
    splitting rules:
    - sentence ends with `TEXT_SPLIT_PUNCTUATIONS` or newline
    - consecutive punctuations are allowed in one sentence
    - ignore punctuations within （）
    """
    # split text
    # TODO sometimes a sentence is too long, consider force splitting even if sentence is not finished
    # remove double newline
    text = text.replace("\n\n", "\n")
    # split by 。or \n
    sentence_buf = []

    while (m := match_first_sentence.match(text)):
        first_sent, text = text[:m.end(0)], text[m.end(0):]
        sentence_buf.append(first_sent)
    
    if text:
        sentence_buf.append(text)
    return sentence_buf


def remove_parathesis(sentence:str, replace=''):
    """remove （）from sentence
    """
    sentence = match_parathesis.sub(replace, sentence)
    sentence = match_parathesis_ascii.sub(replace, sentence)
    return sentence
