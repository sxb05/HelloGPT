from pathlib import Path
from datetime import datetime


from sqlalchemy import create_engine, Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import declarative_base, relationship, sessionmaker



Path("data").mkdir(exist_ok=True)

DATABASE_URL = "sqlite:///data/memory.db"

engine = create_engine(DATABASE_URL,connect_args={"check_same_thread":False},
                        echo=False)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    thread_id = Column(String(255), unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    created_at = Column(String(255), default=datetime.utcnow().isoformat())
    updated_at = Column(String(255), default=datetime.utcnow().isoformat(),
                         onupdate=datetime.utcnow().isoformat())
    # messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    thread_id = Column(String)
    role = Column(String(50), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(String(255), default=datetime.utcnow().isoformat())
    updated_at = Column(String(255), default=datetime.utcnow().isoformat(),
                         onupdate=datetime.utcnow().isoformat())

    conversation = relationship("Conversation", backref="messages")


class LongTermMemory(Base):
    __tablename__ = "long_term_memory"

    id = Column(Integer, primary_key=True, index=True)
    thread_id = Column(String)
    content = Column(Text, nullable=False)
    created_at = Column(String(255), default=datetime.utcnow().isoformat())
    updated_at = Column(String(255), default=datetime.utcnow().isoformat(),
                         onupdate=datetime.utcnow().isoformat())

    conversation = relationship("Conversation", backref="long_term_memories")


def init_db():
    Base.metadata.create_all(bind=engine)



def create_update_convo(thread_id: str, first_message: str, name: str = "New Conversation"):
    session = SessionLocal()
    try:
        conversation = session.query(Conversation).filter_by(thread_id=thread_id).first()
        if conversation:
            conversation.name = name
            conversation.updated_at = datetime.utcnow().isoformat()
        else:
            conversation = Conversation(thread_id=thread_id, name=name)
            session.add(conversation)
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


def list_conversations():
    session = SessionLocal()
    try:
        conversations = session.query(Conversation).order_by(Conversation.updated_at.desc()).all()
        return conversations
    except Exception as e:
        raise e
    finally:
        session.close()



def save_chat_message(thread_id: str, role: str, content: str):
    session = SessionLocal()
    try:
        message = ChatMessage(thread_id=thread_id, role=role, content=content)
        session.add(message)
        conversation = (session.query(Conversation).filter_by(thread_id=thread_id).first())
        if conversation:
            conversation.updated_at = datetime.utcnow().isoformat()
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

def save_memory(thread_id: str, content: str):
    session = SessionLocal()
    try:
        memory = LongTermMemory(thread_id=thread_id, content=content)
        session.add(memory)
        conversation = (session.query(Conversation).filter_by(thread_id=thread_id).first())
        if conversation:
            conversation.updated_at = datetime.utcnow().isoformat()
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
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


def get_chat_history(thread_id: str):
    session = SessionLocal()
    try:
        messages = (session.query(ChatMessage)
                    .filter(ChatMessage.thread_id == thread_id)
                    .order_by(ChatMessage.created_at.asc())
                    .all())
        return messages
    except Exception as e:
        raise e
    finally:
        session.close()