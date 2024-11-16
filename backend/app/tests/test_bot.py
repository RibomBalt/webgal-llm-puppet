import pytest
import subprocess
import signal
import os
import time
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from uuid import uuid1
from ..chat.bot_agent import BotAgent
from ..chat.orm import Base, ChatSession
from ..utils import load_secret

MODEL = os.environ.get("MODEL", "mockai")


@pytest.fixture(scope="module")
def start_mockai():
    if MODEL == "mockai":
        mockai = subprocess.Popen(
            ["npm", "start"], cwd="../mockai", preexec_fn=os.setpgrp
        )
        print(f"::mockai start, pid={mockai.pid}")
        time.sleep(1)

    yield

    if (MODEL == "mockai") and (mockai.poll() is None):
        os.killpg(os.getpgid(mockai.pid), signal.SIGTERM)
        print("::mockai end")


def test_getanswer(start_mockai):
    secret = load_secret(MODEL)
    bot = BotAgent.new_session(
        session_name="test translation",
        secret_key=MODEL,
        system_prompt="Please translate user's input into Chinese",
        model_secret=secret,
    )

    # non stream get answer
    t0 = time.time()
    resp = bot.get_answer("Let's go.", stream=False)
    print(resp, "\n", f"t = {time.time() - t0}")

    # stream get answer

    t0 = time.time()
    resp = bot.get_answer("How are you", stream=True)

    recv_list = []
    for delta in resp:
        recv_list.append(delta)

    print(recv_list, "\n", f"t = {time.time() - t0}")

    print(bot)
    print(bot.to_dict())

    assert all(h.export_message()["role"] == "user" for h in bot.chat_history[::2]), [
        h.export_message()["role"] for h in bot.chat_history[::1]
    ]
    assert all(
        h.export_message()["role"] == "assistant" for h in bot.chat_history[1::2]
    ), [h.export_message()["role"] for h in bot.chat_history[::1]]

    assert str(bot) == str(BotAgent.from_dict(bot.to_dict()))


def test_db_session(start_mockai):
    """ """
    secret = load_secret(MODEL)
    engine = create_engine("sqlite://", echo=True)
    Base.metadata.create_all(engine)

    db_sess = Session(engine)

    # non-exist`
    with pytest.raises(IndexError):
        BotAgent.load_from_db(
            db_sess,
            uuid1(),
            model_secret=secret,
        )

    # new bot
    bot = BotAgent.new_session(
        session_name="test translation",
        secret_key=MODEL,
        system_prompt="Please translate user's input into Chinese",
        model_secret=secret,
    )

    # add a few fake message
    for i in range(40):
        bot.new_message(["user", "assistant"][i % 2], str(i))

    assert bot.unsaved_msg == 40
    bot.save_to_db(db_sess)
    assert bot.unsaved_msg == 0

    chat_sess = ChatSession.load_from_db_by_id(db_sess, bot.chat_session.id)
    assert str(chat_sess) == str(bot.chat_session)

    # load history
    bot2 = BotAgent.load_from_db(db_sess, bot.chat_session.id, secret)
    assert all(
        msg.msg == str(ind)
        for msg, ind in zip(bot2.chat_history[::-1], range(39, -1, -1))
    ), [msg.msg for msg in bot2.chat_history]
    bot2.load_chat_history(db_sess, modify_this_object=True)
    assert all(
        msg.msg == str(ind)
        for msg, ind in zip(bot2.chat_history[::-1], range(39, -1, -1))
    ), [msg.msg for msg in bot2.chat_history]
    assert len(bot2.chat_history) == 40, [msg.msg for msg in bot2.chat_history]

    print(ChatSession.list_session_ids(db_sess))

    for delta in bot2.get_answer("So it rains heavily", stream=True):
        print(delta, end="")

    print([msg.msg for msg in bot2.chat_history])
