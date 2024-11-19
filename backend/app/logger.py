import logging
from flask.logging import default_handler
import os


def log_setup(logger_names, log_level="INFO", log_file="logs/info.log"):
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    file_handler = logging.FileHandler(filename=log_file)

    for logger in logger_names:
        if isinstance(logger, str):
            logger = logging.getLogger(logger)

        logger.addHandler(default_handler)
        logger.addHandler(file_handler)
        logger.setLevel(log_level)
