from flask import Flask
import os
from .chat.orm import db
from .chat import chat as chat_bp
from .logger import log_setup
from .utils import get_environ_int, load_secret


def init_db(app: Flask, db_uri: str):
    """ """
    if db_uri.startswith("sqlite:///"):
        # I don't know why it add an instance dir but this is from strace
        db_file = os.path.join("instance", db_uri[len("sqlite:///") :])
        if not os.path.isfile(db_file):
            os.system(f"touch {db_file}")

    app.config["SQLALCHEMY_DATABASE_URI"] = db_uri
    db.init_app(app)

    with app.app_context():
        db.create_all()

    return db


def create_app():
    is_debug = bool(get_environ_int("DEBUG", True))

    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.urandom(32)
    # load AI token
    # TODO: maybe support change models on the fly
    app.config["MODEL_NAME"] = os.environ.get("MODEL", "mockai")
    app.config["MODEL_SECRETS"] = load_secret(name=None)

    # config
    app.config["HOST"] = os.environ.get("HOST", "127.0.0.1")
    app.config["PORT"] = get_environ_int("PORT", 10228)
    # app.config["WS_PORT"] = get_environ_int("WS_PORT", 10229)
    app.config["DEBUG"] = is_debug

    # orm

    db_uri = os.environ.get("SQLITE_URI", "sqlite:///chat.db")
    db = init_db(app, db_uri)
    app.database = db

    # # session
    # app.config.from_mapping({
    #     "SESSION_TYPE": "redis",
    #     "SESSION_REDIS": Redis(host='localhost', port=6379, db=0),
    #     "SESSION_PERMANENT": True,
    #     "SESSION_BACKUP_PATH": 'redis.snapshot.db'
    # })
    # Session(app)

    # blueprint
    app.register_blueprint(chat_bp)

    # log
    log_setup(
        (
            app.logger,
            "bot",
        ),
        log_level="DEBUG" if is_debug else "INFO",
    )

    return app
