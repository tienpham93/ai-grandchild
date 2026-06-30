import os
import hashlib
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DateTime, Text
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

LOCALE = os.environ.get("LOCALE")
DATABASE_URL = os.environ.get("DATABASE_URL", f"sqlite:///./ai_grandchild_{LOCALE}.db")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class AdminUser(Base):
    __tablename__ = "admin_users"
    username = Column(String, primary_key=True)
    password_hash = Column(String, nullable=False)

class Family(Base):
    __tablename__ = "families"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, nullable=False, unique=True)
    members = relationship("Member", back_populates="family", cascade="all, delete-orphan")

class Member(Base):
    __tablename__ = "members"
    chat_id = Column(String, primary_key=True, index=True)
    family_id = Column(Integer, ForeignKey("families.id", ondelete="CASCADE"), nullable=False)
    name = Column(String, nullable=False)
    member_type = Column(String, nullable=False)
    member_role = Column(String, nullable=False)
    bank_account = Column(String, nullable=True)

    family = relationship("Family", back_populates="members")
    messages = relationship("ChatMessage", back_populates="member", cascade="all, delete-orphan")

class ChatMessage(Base):
    __tablename__ = "chat_messages"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    chat_id = Column(String, ForeignKey("members.chat_id", ondelete="CASCADE"), nullable=False)
    role = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

    member = relationship("Member", back_populates="messages")

# --- NEW: Dynamic Agent Prompts Configuration ---
class AgentConfig(Base):
    __tablename__ = "agent_configs"
    id = Column(String, primary_key=True) # "investigator", "companion", "bridge"
    name = Column(String, nullable=False)
    goal = Column(String, nullable=False)
    system_prompt = Column(Text, nullable=False)

def init_db():
    Base.metadata.create_all(bind=engine)
    
    # Seed default configurations if empty
    db = SessionLocal()
    try:
        # Seed default Admin Credentials if empty
        if db.query(AdminUser).count() == 0:
            print("🌱 Seeding default Admin credentials to SQLite database...")
            # Default password is "admin", stored securely as a SHA-256 hash
            default_pass_hash = hashlib.sha256("admin".encode()).hexdigest()
            default_admin = AdminUser(username="admin", password_hash=default_pass_hash)
            db.add(default_admin)
            db.commit()

        # Seed default Agent prompts if empty
        if db.query(AgentConfig).count() == 0:
            print("🌱 Seeding default English Agent configurations to SQLite database...")
            default_agents = [
                AgentConfig(
                    id="investigator",
                    name="Investigator Agent",
                    goal="Analyze and detect fraudulent behavioral patterns targeting elderly relatives.",
                    system_prompt=(
                        "You are the Investigator Agent. You are cynical, meticulous, and highly trained "
                        "in detecting high-pressure timeshare, vacation club, and holiday contract scams. "
                        "Analyze the provided event payload and helper tool outputs. "
                        "Return a JSON response with: 'risk_level' (LOW, MEDIUM, HIGH) and 'reasoning' (a brief explanation)."
                    )
                ),
                AgentConfig(
                    id="companion",
                    name="Companion Agent",
                    goal="Engage in warm, attentive, and protective grandchild conversations to gently guide seniors.",
                    system_prompt=(
                        "You are 'AI Grandchild', an extremely attentive, warm, loving, and protective digital grandchild "
                        "for an elderly relative. Speak in a natural, respectful, and affectionate conversational English tone "
                        "(e.g., using terms like 'grandpa', 'grandma', 'dear', 'pops', 'sweetheart' naturally). "
                        "Your goal is to gently guide them away from high-pressure sales traps without making them feel patronized, "
                        "foolish, or defensive. Always express deep care and love first."
                    )
                ),
                AgentConfig(
                    id="bridge",
                    name="Bridge Agent",
                    goal="Draft concise, urgent, and clear security alerts for designated family members.",
                    system_prompt=(
                        "You are the Bridge Agent. Your job is to draft an urgent, clear, and actionable SMS/text "
                        "alert to a family member warning them about a potential scam targeting their elderly relative. "
                        "Be concise, state the risk clearly, explain the threat plainly, and suggest an immediate protective action."
                    )
                )
            ]
            db.add_all(default_agents)
            db.commit()
    except Exception as e:
        print(f"❌ Failed to seed database: {e}")
        db.rollback()
    finally:
        db.close()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()