from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session
from sqlalchemy import select
from uuid import uuid1, UUID
from datetime import datetime
import json
import logging

logger = logging.getLogger("bot")


class Base(DeclarativeBase):
    def to_dict(self):
        """used by redis, dict[str,str]"""
        out = {}
        for k, v in self.__dict__.items():
            if k.startswith("_"):
                continue

            if isinstance(v, datetime):
                out[k] = str(v.timestamp())
            elif isinstance(v, UUID):
                out[k] = v.hex
            else:
                out[k] = str(v)

        return out

    @classmethod
    def from_dict(cls, d_: dict):
        d = d_.copy()
        obj = cls(**d)
        return obj

    @classmethod
    def load_from_db_by_id(cls, db_session: Session, id: UUID):
        """get object with given id from database, can return None"""
        return db_session.execute(select(cls).filter_by(id=id)).scalar_one_or_none()

    def __str__(self):
        return json.dumps(self.to_dict())


db = SQLAlchemy(model_class=Base)


class ChatSession(db.Model, Base):
    """
    secret_key: key to access to the Model. Secret (including internal names) are not stored
    model_params: json to pass to kwargs of completion, can include: temperatures, top_p, ...
    """

    id: Mapped[UUID] = mapped_column(primary_key=True, unique=True)
    name: Mapped[str]
    secret_key: Mapped[str]
    system_prompt: Mapped[str]
    model_params: Mapped[str]
    max_memory: Mapped[int]
    last_chat_time: Mapped[datetime]

    @classmethod
    def create(
        cls,
        name,
        secret_key,
        model_params="{}",
        system_prompt="",
        max_memory=30,
        id=None,
    ):
        """generate a message at now"""
        obj = cls()
        if id is None:
            obj.id = uuid1()
        elif isinstance(id, str):
            obj.id = UUID(id)
        else:
            obj.id = id

        obj.name = name
        obj.secret_key = secret_key
        obj.system_prompt = system_prompt
        obj.max_memory = max_memory
        try:
            # check jsonify on create
            json.loads(model_params)
        except json.JSONDecodeError:
            logger.warning(f"{model_params = } is not valid JSON")
            model_params = "{}"

        obj.model_params = model_params
        obj.last_chat_time = datetime.now()

        return obj

    def export_system_prompt(self):
        """ """
        return (
            {"role": "system", "content": self.system_prompt}
            if self.system_prompt
            else None
        )

    @classmethod
    def list_session_ids(cls, db_session: Session):
        return db_session.execute(select(cls.id, cls.last_chat_time)).all()


class ChatMessage(db.Model, Base):
    id: Mapped[UUID] = mapped_column(primary_key=True, unique=True)
    session_id: Mapped[UUID]
    time: Mapped[datetime]
    role: Mapped[str]
    mood: Mapped[str]
    msg: Mapped[str]
    others: Mapped[str]

    def export_message(self):
        """convert to {role, content} type of dict before sending"""
        return {"role": self.role, "content": self.msg}

    @classmethod
    def create(
        cls,
        role: str,
        msg: str,
        session: ChatSession,
        mood="",
        others="{}",
        id=None,
        time=None,
    ):
        """generate a message at now"""
        obj = cls()
        if id is None:
            obj.id = uuid1()
        elif isinstance(id, str):
            obj.id = UUID(id)
        else:
            obj.id = id

        if isinstance(session, ChatSession):
            obj.session_id = session.id
        else:
            obj.session_id = session

        obj.role = role
        obj.msg = msg
        obj.mood = mood
        obj.others = others

        if time is None:
            obj.time = datetime.now()
        else:
            obj.time = time

        return obj

    @classmethod
    def from_dict(cls, d_: dict):
        d = d_.copy()
        d["time"] = datetime.fromtimestamp(float(d["time"]))

        obj = cls(**d)
        return obj
