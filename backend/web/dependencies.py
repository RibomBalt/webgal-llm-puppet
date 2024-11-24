"""All dependencies are called by route, under context"""

from typing import AsyncIterator
from typing_extensions import Annotated
from fastapi import Depends, Query
from aiocache import Cache, caches
from contextlib import asynccontextmanager
from .config import get_settings, AppSettings
from .models.chat import ChatSession
from uuid import UUID
from .logger import web_logger


async def test_cache(cache: Cache):
    await cache.set("test key", "test value")
    v = await cache.get("test key")
    await cache.clear()
    return v


async def init_cache():
    # TODO add an alternative for redis
    settings = get_settings()

    try:
        caches.set_config(
            {
                "default": {
                    "cache": "aiocache.RedisCache",
                    "endpoint": settings.redis_host,
                    "port": settings.redis_port,
                    "password": settings.redis_password,
                    "timeout": 1,
                    "serializer": {"class": "aiocache.serializers.JsonSerializer"},
                    "plugins": [],
                }
            }
        )
        cache = caches.get("default")
        await test_cache(cache)

    except (SystemExit, KeyboardInterrupt):
        raise

    except Exception as err:
        web_logger.warning(
            f"Redis error encountered: ({err}), fallback to simple cache",
            exc_info=False,
        )
        caches.set_config(
            {
                "default": {
                    "cache": "aiocache.SimpleMemoryCache",
                    "serializer": {"class": "aiocache.serializers.JsonSerializer"},
                }
            }
        )

    web_logger.info(f"Cache setup: {caches.get('default')}")
    return True


def get_cache() -> Cache:
    return caches.get("default")


def get_chatsession(
    cache: Annotated[Cache, Depends(get_cache)],
    settings: Annotated[AppSettings, Depends(get_settings)],
    sess_id: UUID = None,
    preset_name: str = "sakiko",
    max_history: int = 30,
    create=False,
    save=True,
):
    """return a async context manager that return a ChatSession object.
    either create a new one or load from cache, and save back to cache afterwards
    """

    @asynccontextmanager
    async def get_bot() -> AsyncIterator[ChatSession | None]:
        """ """
        if create or sess_id is None:
            # new sess
            bot = ChatSession.from_preset(settings.bot_preset.get(preset_name))
        else:
            # load from cache
            # TODO what if not found?
            try:
                bot = await ChatSession.load_from_redis_cache(
                    sess_id=sess_id.hex, cache=cache
                )
            except IndexError:
                bot = None

        yield bot
        # save to cache
        if save and (bot is not None):
            web_logger.debug(f"get_chatsession teardown save cache: {bot.meta.id}")
            await bot.save_to_redis_cache(cache=cache)

    return get_bot()


async def get_lastmood(
    sess_id: UUID,
    msg_id: int,
    cache: Annotated[Cache, Depends(get_cache)],
    first_answer: Annotated[int, Query()] = 0,
):
    """dependable"""
    last_cache_key = f"msgmood:{sess_id.hex}:{msg_id-1}"
    if first_answer == 1:
        last_mood = 'listening'
    # elif msg_id == 1:
    #     # first mood should be happy
    #     last_mood = "高兴"
    elif await cache.exists(last_cache_key):
        last_mood = (await cache.get(last_cache_key)).get("last_mood")
    else:
        # choose random
        last_mood = ""

    return last_mood
