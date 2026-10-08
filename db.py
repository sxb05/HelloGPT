from pathlib import Path
from datetime import datetime


from sqlalchemy import create_engine, Column, Integer, String, Text, ForeignKey, inspect, text
from sqlalchemy.orm import declarative_base, relationship, sessionmaker



Path("data").mkdir(exist_ok=True)

DATABASE_URL = "sqlite:///data/memory.db"

engine = create_engine(DATABASE_URL,connect_args={"check_same_thread":False},
                        echo=False)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def utcnow_iso(_context=None) -> str:
    return datetime.utcnow().isoformat()


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    thread_id = Column(String(255), unique=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    name = Column(String(255), nullable=False)
    created_at = Column(String(255), default=utcnow_iso)
    updated_at = Column(String(255), default=utcnow_iso, onupdate=utcnow_iso)
    messages = relationship("ChatMessage", back_populates="conversation", cascade="all, delete-orphan")
    long_term_memories = relationship(
    "LongTermMemory",
    back_populates="conversation",
    cascade="all, delete-orphan"
)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    thread_id = Column(String,ForeignKey("conversations.thread_id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    role = Column(String(50), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(String(255), default=utcnow_iso)
    updated_at = Column(String(255), default=utcnow_iso, onupdate=utcnow_iso)

    conversation = relationship("Conversation", back_populates="messages")


class LongTermMemory(Base):
    __tablename__ = "long_term_memory"

    id = Column(Integer, primary_key=True, index=True)
    thread_id = Column(String,ForeignKey("conversations.thread_id"))
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    content = Column(Text, nullable=False)
    created_at = Column(String(255), default=utcnow_iso)
    updated_at = Column(String(255), default=utcnow_iso, onupdate=utcnow_iso)

    conversation = relationship("Conversation", back_populates="long_term_memories")


def init_db():
    Base.metadata.create_all(bind=engine)
    inspector = inspect(engine)
    migrations = {
        "conversations": "user_id",
        "chat_messages": "user_id",
        "long_term_memory": "user_id",
    }
    with engine.begin() as connection:
        for table_name, column_name in migrations.items():
            if column_name not in {column["name"] for column in inspector.get_columns(table_name)}:
                connection.execute(
                    text(
                        f"ALTER TABLE {table_name} ADD COLUMN {column_name} "
                        "INTEGER REFERENCES users(id)"
                    )
                )


def create_update_convo(
    thread_id: str, user_id: int, first_message: str, name: str = "New Conversation"
) -> bool:
    session = SessionLocal()
    try:
        conversation = session.query(Conversation).filter_by(thread_id=thread_id).first()
        if conversation:
            if conversation.user_id != user_id:
                return False
            conversation.name = name
            conversation.updated_at = datetime.utcnow().isoformat()
        else:
            conversation = Conversation(thread_id=thread_id, user_id=user_id, name=name)
            session.add(conversation)
        session.commit()
        return True
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


def conversation_belongs_to_user(thread_id: str, user_id: int) -> bool:
    session = SessionLocal()
    try:
        return (
            session.query(Conversation)
            .filter_by(thread_id=thread_id, user_id=user_id)
            .first()
            is not None
        )
    finally:
        session.close()


def list_conversations(user_id: int):
    session = SessionLocal()
    try:
        conversations = (session.query(Conversation)
                         .filter(Conversation.user_id == user_id)
                         .order_by(Conversation.updated_at.desc()).all())
        return conversations
    except Exception as e:
        raise e
    finally:
        session.close()



def save_chat_message(thread_id: str, user_id: int, role: str, content: str) -> bool:
    session = SessionLocal()
    try:
        conversation = (session.query(Conversation)
                        .filter_by(thread_id=thread_id, user_id=user_id).first())
        if conversation is None:
            return False
        message = ChatMessage(
            thread_id=thread_id, user_id=user_id, role=role, content=content
        )
        session.add(message)
        conversation.updated_at = datetime.utcnow().isoformat()
        session.commit()
        return True
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

def save_memory(thread_id: str, content: str):
    session = SessionLocal()
    print("🔥 SAVE MEMORY TOOL CALLED:", content)
    try:
        conversation = (
            session.query(Conversation)
            .filter_by(thread_id=thread_id)
            .first()
        )

        if not conversation:
            raise ValueError(
                f"Conversation with thread_id '{thread_id}' does not exist"
            )

        memory = LongTermMemory(
            thread_id=thread_id,
            user_id=conversation.user_id,
            content=content
        )

        session.add(memory)

        conversation.updated_at = datetime.utcnow().isoformat()

        session.commit()

    except Exception:
        session.rollback()
        raise

    finally:
        session.close()


def search_memory(thread_id: str, query: str):
    session = SessionLocal()
    try:
        memories = (session.query(LongTermMemory)
                    .filter(LongTermMemory.thread_id == thread_id,
                            LongTermMemory.content.contains(query))
                    .all())
        return memories
    except Exception as e:
        raise e
    finally:
        session.close()


def get_chat_history(thread_id: str, user_id: int):
    session = SessionLocal()
    try:
        messages = (session.query(ChatMessage)
                    .filter(ChatMessage.thread_id == thread_id,
                            ChatMessage.user_id == user_id)
                    .order_by(ChatMessage.created_at.asc())
                    .all())
        return messages
    except Exception as e:
        raise e
    finally:
        session.close()


def delete_conversation(thread_id: str, user_id: int) -> bool:
    session = SessionLocal()
    try:
        conversation = (session.query(Conversation)
                        .filter_by(thread_id=thread_id, user_id=user_id).first())
        if conversation is None:
            return False
        session.delete(conversation)
        session.commit()
        return True
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()