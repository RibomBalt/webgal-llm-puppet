from ..chat.orm import ChatMessage, ChatSession
import json


def test_session_msg():
    new_sess = ChatSession.create("mockai", "mockai", system_prompt="this is system")
    assert str(ChatSession.from_dict(new_sess.to_dict())) == json.dumps(
        new_sess.to_dict()
    )

    new_msg = ChatMessage.create(role="user", msg="hahah", session=new_sess)
    assert str(ChatMessage.from_dict(new_msg.to_dict())) == json.dumps(
        new_msg.to_dict()
    )
