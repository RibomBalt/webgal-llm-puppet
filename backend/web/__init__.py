from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
# from .chat.orm import db
# from .chat.bot_agent import ChatBot
# from .chat import chat as chat_bp, webgal
import logging
from .logger import log_setup
from .routes.webgal_route import webgal_route
from .routes.api import api_route
from .config import get_settings
from .dependencies import init_cache
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_cache()
    yield


def create_app():
    settings = get_settings()
    app = FastAPI(debug=settings.debug, lifespan=lifespan)
    app.state.settings = settings

    app.add_middleware(
        CORSMiddleware,
        allow_origins=['*'],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    for logger_name in ("web", "model", "bot"):
        log_setup(logger_name, log_level="DEBUG" if settings.debug else "INFO")

    app.include_router(webgal_route)
    app.include_router(api_route)
    # staticfile in current fastapi 0.115.5 seems buggy on APIrouters
    # https://github.com/fastapi/fastapi/discussions/9070
    app.mount("/static", StaticFiles(directory="web/static"), name="static")

    # log
    app.state.logger = logging.getLogger("web")

    return app
