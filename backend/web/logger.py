import logging
import os


def log_setup(logger: str | logging.Logger, log_level="INFO", log_file="logs/info.log"):
    os.makedirs(os.path.dirname(log_file), exist_ok=True)

    formatter = logging.Formatter('|%(asctime)s|%(name)s|%(levelname)s|: %(message)s')
    file_handler = logging.FileHandler(filename=log_file)
    term_handler = logging.StreamHandler()
    file_handler.setFormatter(formatter)
    term_handler.setFormatter(formatter)

    if isinstance(logger, str):
        logger = logging.getLogger(logger)

    logger.addHandler(file_handler)
    logger.addHandler(term_handler)
    logger.setLevel(log_level)

    return logger

bot_logger = logging.getLogger('bot')
model_logger = logging.getLogger('model')
web_logger = logging.getLogger('web')
