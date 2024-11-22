from fastapi import (
    APIRouter,
    Path,
    Query,
    Depends,
    BackgroundTasks,
)
from fastapi.responses import RedirectResponse
from typing import AsyncIterator
from fastapi.responses import PlainTextResponse
from typing import Annotated
from ..dependencies import Cache, get_cache, get_chatsession, get_lastmood
from ..models.chat import ChatSession
from ..models.bot import L2dBotPreset
from ..config import AppSettings, get_settings
from ..logger import web_logger
from ..webgal_utils import TEXT_SPLIT_PUNCTUATIONS, text_split_sentence
import jinja2
import asyncio
from uuid import UUID

webgal_route = APIRouter(prefix="/webgal")
jinja2_env = jinja2.Environment(loader=jinja2.FileSystemLoader("web/templates"))


@webgal_route.get("/")
async def health():
    return "ok"


def exit_script():
    return jinja2_env.get_template("error.txt").render()

async def bye_script(preset:L2dBotPreset, last_mood:str = ""):
    
    motion, expression = preset.random_motion(last_mood).split(":")
    template = jinja2_env.get_template("bye.txt")
    script = template.render(
        msg = preset.bye_message,
        motion=motion,
        expression=expression,
        l2d_path=preset.live2d_model_path,
        speaker=preset.speaker,
    )

    return script

async def pending_script(
    sess_id: UUID,
    msg_id: int,
    preset: L2dBotPreset,
    settings: AppSettings,
    preset_name: str,
    last_mood: str
):
    """ """
    motion, expression = preset.random_motion(last_mood).split(":")
    next_jump_url = next_jump_url = (
        f"http://{settings.host}:{settings.port}/webgal/next.txt/{sess_id.hex}/{msg_id}?bot={preset_name}"
    )

    template = jinja2_env.get_template("pending.txt")
    script = template.render(
        sess_id=sess_id.hex,
        motion=motion,
        expression=expression,
        l2d_path=preset.live2d_model_path,
        next_url=next_jump_url,
    )

    return script


async def msg_mood_to_script(
    settings: Annotated[AppSettings, Depends(get_settings)],
    sess_id: UUID,
    msg_mood_list: list[tuple[str, str]],
    msg_id: int,
    preset_name: Annotated[str, Query(alias="bot")] = "sakiko",
    cache: Annotated[Cache, Depends(get_cache)] = None,
    require_input=False,
):
    """convert (msg,mood) tuples to a webgal script"""
    preset = settings.bot_preset.get(preset_name)

    # choose motion/expression set
    msg_list = []
    motion_list = []
    expression_list = []
    for msg, mood in msg_mood_list:
        msg_list.append(msg)
        motion, expression = preset.random_motion(mood).split(":")
        motion_list.append(motion)
        expression_list.append(expression)

    if require_input:
        this_template = "new_input.txt"
        next_endpoint = "chat.txt"
    else:
        this_template = "answer.txt"
        next_endpoint = "next.txt"

    next_jump_url = f"http://{settings.host}:{settings.port}/webgal/{next_endpoint}/{sess_id.hex}/{msg_id + 1}?bot={preset_name}"

    # listening is a pending action when waiting for
    listening = preset.random_motion("listening").split(":")

    template = jinja2_env.get_template(this_template)
    script = template.render(
        sess_id=sess_id.hex,
        msg_motion_expression_list=zip(msg_list, motion_list, expression_list),
        l2d_path=preset.live2d_model_path,
        speaker=preset.speaker,
        next_url=next_jump_url,
        listening=listening,
    )

    web_logger.debug(f"generate {sess_id}/{msg_id}:\n{script}")
    if cache is not None:
        # we should cache the results
        # NOTE: if this message has no messages (unlikely), fallback to listening
        result_to_cache = {
            "script": script,
            "last_mood": msg_mood_list[-1][1]
            if len(msg_mood_list) > 0
            else "listening",
        }
        cache_key = f"msgmood:{sess_id.hex}:{msg_id}"
        web_logger.debug(f"caching {result_to_cache} to {cache_key}")
        await cache.set(cache_key, result_to_cache)

    return script


async def get_mood_for_sentence(
    mood_bot: ChatSession, prompt: str, settings: AppSettings
):
    """get mood for a single sentence, nothing else"""
    mood_gen = (await mood_bot.get_answer_a(
        settings=settings, prompt=prompt, preset_name="mood_analyzer"
    ))()
    mood = ""
    async for mood_chunk in mood_gen:
        if mood_chunk is not None:
            mood += mood_chunk
        else:
            break

    return mood


async def task_get_chat_response_and_mood(
    resp_gen: AsyncIterator[str | None],
    settings: Annotated[AppSettings, Depends(get_settings)],
    cache: Annotated[Cache, Depends(get_cache)],
    msg_id: int,
    sess_id: UUID,
):
    """ """
    # create a mood bot, we don't cache it
    async with get_chatsession(
        create=True,
        save=False,
        preset_name="mood_analyzer",
        settings=settings,
        cache=cache,
    ) as mood_bot:
        remn_text = ""
        async for chunk in resp_gen:
            if chunk is None:
                # we reach the end of this generator
                break
            elif len(chunk) == 0:
                # we don't process empty strings
                continue

            remn_text += chunk
            # test whether we should split
            # we use this because this is slightly quicker than actually try to split it
            if any(c in TEXT_SPLIT_PUNCTUATIONS for c in chunk):
                sentences = text_split_sentence(remn_text)
                for sent in sentences[:-1]:
                    # each sent is a complete sentence
                    # here we block the mood analyzer (since this is threaded background)
                    if mood_bot is not None:
                        mood = await get_mood_for_sentence(
                            prompt=sent, settings=settings, mood_bot=mood_bot
                        )

                    else:
                        # this is a fallback for bot returning invalid mood
                        mood = ""

                    web_logger.debug(f"mood analyze: {sent}|{mood}|")
                    # now we have a set of sent, mood for next round, send them to next
                    # TODO now send to cache every sentence, should we batch it?
                    await msg_mood_to_script(
                        settings=settings,
                        sess_id=sess_id,
                        msg_mood_list=[(sent, mood)],
                        msg_id=msg_id,
                        require_input=False,
                        cache=cache,
                    )
                    msg_id += 1

                # last sentence might be not complete
                remn_text = sentences[-1]

        # now remn text might still be non empty
        if remn_text:
            if mood_bot is not None:
                mood = await get_mood_for_sentence(
                    prompt=remn_text, settings=settings, mood_bot=mood_bot
                )
            else:
                # this is a fallback for bot returning invalid mood
                mood = ""
        else:
            mood = ""

        final_msg_mood_list = [(remn_text, mood)] if remn_text else []
        # but we should always return a require_input=True
        await msg_mood_to_script(
            settings=settings,
            sess_id=sess_id,
            msg_mood_list=final_msg_mood_list,
            msg_id=msg_id,
            require_input=True,
            cache=cache,
        )
        msg_id += 1


@webgal_route.get("/newchat.txt", response_class=PlainTextResponse)
async def new_session(
    settings: Annotated[AppSettings, Depends(get_settings)],
    cache: Annotated[Cache, Depends(get_cache)],
    preset_name: Annotated[str, Query(alias="bot")] = "sakiko",
):
    """create a new chat
    preset_name: can choose a specific preset
    """
    async with get_chatsession(
        settings=settings, cache=cache, create=True, preset_name=preset_name
    ) as bot:
        preset = settings.bot_preset.get(preset_name)
        web_logger.debug(f"{settings.bot_preset}, {preset}")
        #
        resp = await msg_mood_to_script(
            settings=settings,
            sess_id=bot.meta.id,
            msg_mood_list=[(preset.welcome_message, next(iter(preset.mood.keys())))],
            msg_id=0,
            require_input=True,
        )

    return resp


@webgal_route.get("/next.txt/{sess_id}/{msg_id}", response_class=PlainTextResponse)
async def continue_content(
    sess_id: Annotated[UUID, Path()],
    msg_id: Annotated[int, Path()],
    settings: Annotated[AppSettings, Depends(get_settings)],
    last_mood: Annotated[str, Depends(get_lastmood)],
    cache: Annotated[Cache, Depends(get_cache)],
    preset_name: Annotated[str, Query(alias="bot")] = "sakiko",
):
    """ """
    cache_key = f"msgmood:{sess_id.hex}:{msg_id}"
    for _ in range(5):
        result_from_cache = await cache.get(cache_key, None)
        if result_from_cache is not None:
            break
        await asyncio.sleep(0.5)
    else:
        # TODO return a pending script rather than exit
        web_logger.debug(f"{cache_key} not hit")
        preset = settings.bot_preset.get(preset_name)
        return await pending_script(
            sess_id=sess_id,
            msg_id=msg_id,
            last_mood=last_mood,
            preset=preset,
            preset_name=preset_name,
            settings=settings,
        )

    web_logger.debug(f"get a cache result: {result_from_cache}")

    return result_from_cache.get("script")


@webgal_route.get("/chat.txt/{sess_id}/{msg_id}", response_class=PlainTextResponse)
async def chat_llm(
    background_tasks: BackgroundTasks,
    settings: Annotated[AppSettings, Depends(get_settings)],
    cache: Annotated[Cache, Depends(get_cache)],
    last_mood: Annotated[str, Depends(get_lastmood)],
    sess_id: Annotated[UUID, Path()],
    msg_id: Annotated[int, Path()],
    preset_name: Annotated[str, Query(alias="bot")] = "sakiko",
    prompt: Annotated[str, Query(alias="p")] = "",
):
    """talk with bot, add background task to fill caches, return a pending"""
    async with get_chatsession(
        sess_id=sess_id, settings=settings, cache=cache, preset_name=preset_name
    ) as bot:
        preset = settings.bot_preset.get(preset_name)
        if bot is None:
            web_logger.error(f"bot {sess_id} not successful get", exc_info=True)
            return exit_script()

        if prompt == '再见':
            # byebye sakiko
            web_logger.debug(f"before bye script: {last_mood = }")
            return await bye_script(preset=preset,last_mood=last_mood)

        resp_gen = (await bot.get_answer_a(
            settings=settings,
            prompt=prompt,
            preset_name=preset_name,
        ))(cache=cache)
        web_logger.debug(f"background task for {sess_id}:{msg_id} added")
        background_tasks.add_task(
            task_get_chat_response_and_mood,
            resp_gen=resp_gen,
            settings=settings,
            cache=cache,
            msg_id=msg_id,
            sess_id=sess_id,
        )

    redirect_url = f"/webgal/next.txt/{sess_id.hex}/{msg_id}?bot={preset_name}"
    return RedirectResponse(url=redirect_url)
