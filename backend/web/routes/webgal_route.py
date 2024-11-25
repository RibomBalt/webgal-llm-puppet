from fastapi import (
    APIRouter,
    Path,
    Query,
    Depends,
    BackgroundTasks,
    HTTPException,
    Response
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
from ..tts import tts
import jinja2
import asyncio
import hashlib
from uuid import UUID

webgal_route = APIRouter(prefix="/webgal")
jinja2_env = jinja2.Environment(loader=jinja2.FileSystemLoader("web/templates"))


@webgal_route.get("/")
async def health():
    return "ok"


def exit_script():
    return jinja2_env.get_template("error.txt").render()


async def bye_script(preset: L2dBotPreset, last_mood: str = "", bye_message:str=""):
    # random motion/expression based on last_mood
    motion, expression = preset.random_motion(last_mood).split(":")
    # if bye message is not given
    if not bye_message:
        bye_message = preset.bye_message

    template = jinja2_env.get_template("bye.txt")
    script = template.render(
        msg=bye_message,
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
    last_mood: str,
    next_jump_url: str = "",
):
    """ """
    motion, expression = preset.random_motion(last_mood).split(":")
    if not next_jump_url:
        # default next jump
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


def get_voice_cachekey(sess_id: str, msg: str = '', length=12, hash=None):
    if hash is None:
        hash = hashlib.md5(msg.encode()).hexdigest()[:length]

    return f"voice:{sess_id}:{hash}"


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
    voice_list = []
    for msg, mood in msg_mood_list:
        msg_list.append(msg)
        motion, expression = preset.random_motion(mood).split(":")
        motion_list.append(motion)
        expression_list.append(expression)

        # we put tts while processing every sentences (normally there would be only one)
        voice_content = await tts(msg, preset.voice)
        # TODO make a null sound
        voice_cachekey = get_voice_cachekey(msg=msg, sess_id=sess_id.hex)
        if voice_content and (cache is not None):
            await cache.set(voice_cachekey, voice_content)
            web_logger.debug(f"tts cached: {voice_cachekey}")

        voice_url = f"http://{settings.host}:{settings.port}/webgal/voice.mp3/{sess_id.hex}/{voice_cachekey.split(':', maxsplit=2)[2]}"
        voice_list.append(voice_url)

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
        msg_motion_expression_list=zip(msg_list, motion_list, expression_list, voice_list),
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
        web_logger.debug(f"caching message chunk to {cache_key}")
        await cache.set(cache_key, result_to_cache)

    return script


async def get_mood_for_sentence(
    mood_bot: ChatSession, prompt: str, settings: AppSettings
):
    """get mood for a single sentence, nothing else"""
    mood_gen = (
        await mood_bot.get_answer_a(
            settings=settings, prompt=prompt, preset_name="mood_analyzer"
        )
    )()
    mood = ""
    async for mood_chunk in mood_gen:
        if mood_chunk is not None:
            mood += mood_chunk
        else:
            break

    web_logger.debug(f"mood query: {prompt}|{mood}|")
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
        web_logger.debug(f"request new bot, preset={preset_name}")
        #
        resp = await msg_mood_to_script(
            settings=settings,
            sess_id=bot.meta.id,
            msg_mood_list=[(preset.welcome_message, '高兴')],
            msg_id=0,
            cache=cache,
            preset_name=preset_name,
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
    pending_counter: Annotated[int, Query(alias='n')] = 0,
    first_answer: Annotated[int, Query()] = 0,
):
    """
    first_answer: 1 if redirected by chat.txt (first response), so pending scripts should respond with last_mood "listening"
    """
    preset = settings.bot_preset.get(preset_name)
    cache_key = f"msgmood:{sess_id.hex}:{msg_id}"
    for _ in range(5):
        result_from_cache = await cache.get(cache_key, None)
        if result_from_cache is not None:
            break
        await asyncio.sleep(0.5)
    else:
        if pending_counter < 10:
            # return a pending script rather than exit if answer is not ready
            web_logger.debug(f"req next.txt: {cache_key} not hit")
            next_jump_url = (
                f"http://{settings.host}:{settings.port}/webgal/next.txt/{sess_id.hex}/{msg_id}?bot={preset_name}&n={pending_counter + 1}"
            )
            return await pending_script(
                sess_id=sess_id,
                msg_id=msg_id,
                last_mood=last_mood,
                preset=preset,
                preset_name=preset_name,
                settings=settings,
                next_jump_url=next_jump_url,
            )
        else:
            # fail to hit cache too many times, backend might be down
            return await bye_script(preset=preset, last_mood=last_mood, bye_message="看来您那里信号很不好呢，我这边先挂了，祝您生活愉快。")

    web_logger.debug(f"get a cache result of {sess_id}/{msg_id}")

    return result_from_cache.get("script")


@webgal_route.get("/chat.txt/{sess_id}/{msg_id}", response_class=PlainTextResponse)
async def chat_llm(
    background_tasks: BackgroundTasks,
    settings: Annotated[AppSettings, Depends(get_settings)],
    cache: Annotated[Cache, Depends(get_cache)],
    last_mood: Annotated[str, Depends(get_lastmood)],
    sess_id: Annotated[UUID, Path()],
    msg_id: Annotated[int, Path()],
    pending: Annotated[str, Query(alias="pending")],
    preset_name: Annotated[str, Query(alias="bot")] = "sakiko",
    prompt: Annotated[str, Query(alias="p")] = "",
):
    """talk with bot, add background task to fill caches, return a pending"""
    async with get_chatsession(
        sess_id=sess_id, settings=settings, cache=cache, preset_name=preset_name
    ) as bot:
        preset = settings.bot_preset.get(preset_name)

        web_logger.debug(f"pending_status: {pending}")
        if bot is None:
            web_logger.error(f"bot {sess_id} not successful get", exc_info=True)
            return exit_script()

        elif prompt == "再见":
            # byebye sakiko
            web_logger.debug(f"before bye script: {last_mood = }")
            return await bye_script(preset=preset, last_mood=last_mood)

        elif prompt == "{prompt}" or pending != '1':
            # prefetching on newchat means the input is still not updated
            # prefetching URL don't parse templates, so we can distinguish them
            web_logger.debug(f"prefetching on newchat: {sess_id}/{msg_id}")
            next_url = f"http://{settings.host}:{settings.port}/webgal/chat.txt/{sess_id.hex}/{msg_id}?bot={preset_name}"
            return await pending_script(
                preset=preset,
                settings=settings,
                last_mood=last_mood,
                sess_id=sess_id,
                msg_id=msg_id,
                preset_name=preset_name,
                next_jump_url=next_url,
            )

        resp_gen = (
            await bot.get_answer_a(
                settings=settings,
                prompt=prompt,
                preset_name=preset_name,
            )
        )(cache=cache)
        web_logger.debug(f"background task for {sess_id}:{msg_id} added")
        background_tasks.add_task(
            task_get_chat_response_and_mood,
            resp_gen=resp_gen,
            settings=settings,
            cache=cache,
            msg_id=msg_id,
            sess_id=sess_id,
        )

    redirect_url = f"/webgal/next.txt/{sess_id.hex}/{msg_id}?bot={preset_name}&first_answer=1"
    return RedirectResponse(url=redirect_url)

@webgal_route.get("/voice.mp3/{sess_id}/{voice_key}")
async def get_voice_file(
    sess_id: Annotated[UUID, Path()],
    voice_key: Annotated[str, Path()],
    settings: Annotated[AppSettings, Depends(get_settings)],
    cache: Annotated[Cache, Depends(get_cache)],
):
    """
    """
    # since we put voice in cache before we respond scripts, we won't wait for voice to be available
    cache_key = get_voice_cachekey(hash=voice_key, sess_id=sess_id.hex)
    result_from_cache = await cache.get(cache_key, None)
    if result_from_cache is not None:
        web_logger.debug(f"tts cache hit: {cache_key}")
        return Response(content=result_from_cache, media_type="audio/mpeg")
    else:
        web_logger.debug(f"tts fail to hit: {cache_key}")
        raise HTTPException(404, f"voice {cache_key} not found")