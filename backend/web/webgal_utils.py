import logging

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
