import pytest
from ..config import get_settings
from ..models.chat import ChatSession
from ..dependencies import get_cache
import json
import asyncio

@pytest.fixture
def settings():
    settings = get_settings()
    print(settings)

    return settings

@pytest.fixture
def cache():
    return get_cache()


async def _test_chat(chat_session: ChatSession, cache):
    await chat_session.save_to_redis_cache(cache)

    resp_gen = await chat_session.get_answer_a(prompt="你好呀", settings=get_settings())
    async for msg in resp_gen:
        print(f"|{msg}|")

    await chat_session.save_to_redis_cache(cache)

    chat_session2 = await ChatSession.load_from_redis_cache(chat_session.meta.id, cache)

    return chat_session2


def test_chats(settings, cache):
    assert 'sakiko' in settings.bot_preset
    sess = ChatSession.from_preset(settings.bot_preset.get('sakiko'))
    sess.add_message('user', 'test response.')
    print(sess)

    # test serialization
    ser_sess = sess.model_dump_json()
    ser_sess_text = json.dumps(ser_sess, )
    sess_new = ChatSession.model_validate_json(json.loads(ser_sess_text))
    sess_new = ChatSession.model_validate_json(ser_sess)

    print(sess_new)

    assert sess_new == sess

    # test cache

    loop = asyncio.get_event_loop()
    sess_new2 = loop.run_until_complete(_test_chat(sess_new, cache))
    assert sess_new == sess_new2
    assert len(sess_new2.messages) == 4

    print([(msg.role, msg.msg) for msg in sess_new2.messages])
