import pytest
import asyncio
from ..dependencies import init_cache, get_cache

@pytest.fixture
def cache():
    init_cache()

    cache = get_cache()

    return cache


def test_cache(cache):
    """
    """

    print(cache)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(cache.set('test key', 'test value'))

    