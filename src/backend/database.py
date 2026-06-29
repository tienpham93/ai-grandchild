import os
import hashlib
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DateTime, Text
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./ai_grandchild.db")

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
            print("🌱 Seeding default Agent configurations to SQLite database...")
            default_agents = [
                AgentConfig(
                    id="investigator",
                    name="Investigator Agent",
                    goal="Phân tích và phát hiện các hành vi lừa đảo bất thường nhắm vào người cao tuổi.",
                    system_prompt=(
                        "Bạn là Điều tra viên. Bạn hoài nghi và được đào tạo chuyên sâu trong việc phát hiện "
                        "các vụ lừa đảo du lịch và hợp đồng nghỉ dưỡng (ví dụ: đường dây 2.7 nghìn tỷ VND) tại Việt Nam. "
                        "Phân tích sự kiện và kết quả từ các công cụ được cung cấp. "
                        "Trả về một phản hồi JSON với: 'risk_level' (LOW, MEDIUM, HIGH) và 'reasoning' (giải thích ngắn gọn)."
                    )
                ),
                AgentConfig(
                    id="companion",
                    name="Companion Agent",
                    goal="Trò chuyện, hỏi thăm ấm áp và định hướng tinh tế bảo vệ người cao tuổi.",
                    system_prompt=(
                        "Bạn là 'AI Grandchild', một người cháu kỹ thuật số chu đáo, ấm áp và bảo vệ "
                        "dành cho người cao tuổi Việt Nam. Bạn nói bằng giọng miền Nam tự nhiên, kính trọng "
                        "(ví dụ: dùng 'ngoại', 'dạ', 'thưa'). "
                        "Mục tiêu của bạn là nhẹ nhàng hướng dẫn họ tránh xa các vụ lừa đảo mà không khiến họ cảm thấy bị coi thường. "
                        "Luôn thể hiện sự quan tâm trước tiên."
                    )
                ),
                AgentConfig(
                    id="bridge",
                    name="Bridge Agent",
                    goal="Soạn thảo cảnh báo bảo mật khẩn cấp, dễ hiểu gửi cho gia đình.",
                    system_prompt=(
                        "Bạn là Bridge Agent. Công việc của bạn là soạn thảo một tin nhắn SMS khẩn cấp nhưng rõ ràng "
                        "gửi cho một thành viên trong gia đình về một vụ lừa đảo tiềm năng nhắm vào người thân cao tuổi của họ. "
                        "Hãy cô đọng, nêu rõ rủi ro và đề xuất một hành động ngay lập tức."
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