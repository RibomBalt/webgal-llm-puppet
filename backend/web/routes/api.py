from fastapi import (
    APIRouter,
    Path,
    Body,
    Query,
    Depends,
    HTTPException,
)
from fastapi.responses import StreamingResponse
from typing import Annotated
from ..dependencies import Cache, get_cache, get_chatsession
from ..config import AppSettings, get_settings
from ..logger import web_logger
import jinja2
from uuid import UUID

api_route = APIRouter(prefix="/api")
jinja2_env = jinja2.Environment(loader=jinja2.FileSystemLoader("web/templates"))


@api_route.get("/newchat")
async def new_session(
    settings: Annotated[AppSettings, Depends(get_settings)],
    cache: Annotated[Cache, Depends(get_cache)],
    preset_name: Annotated[str, Query(alias="bot")] = "sakiko",
    system_prompt: Annotated[str, Query(alias="system")] = "",
    welcome: Annotated[str, Query(alias="welcome")] = "",
):
    """create a new chat
    preset_name: can choose a specific preset
    """

    async with get_chatsession(
        settings=settings, cache=cache, create=True, preset_name=preset_name
    ) as bot:
        # overwrite system prompts / welcome messages
        if system_prompt:
            bot.meta.system_prompt = system_prompt
        if welcome:
            if bot.messages:
                # change already added messages
                bot.messages[-1].msg = welcome
                bot.non_cached = 1
            else:
                # add new welcome messages
                bot.add_message('assistant', welcome)
            
        web_logger.debug(f"request new bot, preset={preset_name}")
        #
        resp = {
            "sess_id": bot.meta.id.hex,
            "system_prompt": bot.meta.system_prompt,
            "welcome": bot.messages[-1].msg 
        }

    return resp

@api_route.post("/chat/{sess_id}")
async def continue_chat(
    sess_id: Annotated[UUID, Path()],
    msg: Annotated[str, Body()],
    settings: Annotated[AppSettings, Depends(get_settings)],
    cache: Annotated[Cache, Depends(get_cache)],
    preset_name: Annotated[str, Query(alias="bot")] = "sakiko",
):
    """get prompt, ask for answer, streaming back
    """
    async with get_chatsession(
        settings=settings, cache=cache, sess_id=sess_id, preset_name=preset_name
    ) as bot:
        if bot is None:
            raise HTTPException(404, f"session {sess_id} not found")

        async def stream_answer():
            async for chunk in (await bot.get_answer_a(settings=settings, prompt=msg, preset_name=preset_name))(cache=cache):
                if chunk is not None:
                    yield chunk
                    
        return StreamingResponse(stream_answer(), )