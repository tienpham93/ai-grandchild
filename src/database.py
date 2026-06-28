import os
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DateTime, Text
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./ai_grandchild.db")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Family(Base):
    __tablename__ = "families"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, nullable=False, unique=True)
    
    # Relationship to members of this family
    members = relationship("Member", back_populates="family", cascade="all, delete-orphan")

class Member(Base):
    __tablename__ = "members"
    chat_id = Column(String, primary_key=True, index=True) # Telegram Unique Identifier
    family_id = Column(Integer, ForeignKey("families.id", ondelete="CASCADE"), nullable=False)
    name = Column(String, nullable=False)
    member_type = Column(String, nullable=False)  # "senior" or "non_senior"
    member_role = Column(String, nullable=False)  # "grandpa", "grandma", "mom", "dad", etc.
    bank_account = Column(String, nullable=True)  # <-- NEW: Optional linked bank account

    family = relationship("Family", back_populates="members")
    messages = relationship("ChatMessage", back_populates="member", cascade="all, delete-orphan")
    
class ChatMessage(Base):
    __tablename__ = "chat_messages"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    chat_id = Column(String, ForeignKey("members.chat_id", ondelete="CASCADE"), nullable=False)
    role = Column(String, nullable=False)  # "user" (Grandpa/Family) or "model" (AI Grandchild)
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

    member = relationship("Member", back_populates="messages")

def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()