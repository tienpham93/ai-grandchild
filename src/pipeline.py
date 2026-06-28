from sqlalchemy.orm import Session
from telegram import Bot
from telegram.error import TelegramError

# Project Modules
from src.config import get_telegram_bot_token
from src.database import get_db, Member, ChatMessage
from src.skills.anonymizer import scrub_pii
from src.agents.investigator import analyze_risk
from src.agents.companion import generate_companion_response, generate_family_response
from src.agents.bridge import format_family_alert

# Init Telegram Bot client
TELEGRAM_BOT_TOKEN = get_telegram_bot_token()
bot = Bot(TELEGRAM_BOT_TOKEN) if TELEGRAM_BOT_TOKEN else None

async def process_chat_event(json_payload: dict, chat_id: str):
    """
    Main background driver coordinating role detection, state logging, 
    and task execution.
    """
    db = next(get_db())
    try:
        member = db.query(Member).filter(Member.chat_id == chat_id).first()
        if not member:
            print(f"⚠️ [Pipeline] Chat ID {chat_id} became unregistered during queue delay.")
            return

        user_msg = json_payload.get("message_text", "")
        _save_message(db, chat_id, role="user", content=user_msg)
        
        # Pull history for context-aware model prompt generation
        history = _get_chat_history(db, chat_id, limit=10)

        if member.member_type == "non_senior":
            await _execute_family_flow(db, member, user_msg, chat_id, history)
        elif member.member_type == "senior":
            await _execute_senior_flow(db, member, user_msg, chat_id, history, json_payload)

    except Exception as e:
         print(f"❌ [Pipeline] Execution error: {e}")
    finally:
        db.close()

# --- Internal Pipeline Helper Functions ---

def _save_message(db: Session, chat_id: str, role: str, content: str):
    """Persists a single message state securely to the SQLite DB."""
    try:
        msg = ChatMessage(chat_id=chat_id, role=role, content=content)
        db.add(msg)
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"❌ [Pipeline DB] Failed to save chat history: {e}")

def _get_chat_history(db: Session, chat_id: str, limit: int = 10) -> list[dict]:
    """Retrieves and formats chronologically sorted message history."""
    history_msgs = db.query(ChatMessage).filter(ChatMessage.chat_id == chat_id).order_by(ChatMessage.timestamp.desc()).limit(limit).all()
    history_msgs.reverse()
    return [{"role": m.role, "content": m.content} for m in history_msgs]

async def _send_telegram_reply(chat_id: str, text: str):
    """Dispatches a basic text message reply back to a user via the Bot API."""
    if not bot:
        print(f"⚠️ [Telegram API] Skipping reply to {chat_id} (No Token).")
        return
    try:
        await bot.send_message(chat_id=chat_id, text=text)
    except TelegramError as e:
        print(f"❌ [Telegram API] Send failed to {chat_id}: {e}")

async def _execute_family_flow(db: Session, member: Member, user_msg: str, chat_id: str, history: list[dict]):
    """Generates and sends a reassuring assistant update to a Family Member."""
    print(f"\n👨‍👩‍👧‍👦 FAMILY INBOUND [{member.name} ({member.member_role})]: {user_msg}")
    
    reply = generate_family_response(history, member.member_role, member.name)
    print(f"   Reply: {reply}")
    
    _save_message(db, chat_id, role="model", content=reply)
    await _send_telegram_reply(chat_id, reply)

async def _execute_senior_flow(db: Session, member: Member, user_msg: str, chat_id: str, history: list[dict], raw_payload: dict):
    """Executes the core anti-fraud evaluation and grandchild response loop."""
    print(f"\n👴 SENIOR INBOUND [{member.name} ({member.member_role})]: {user_msg}")
    
    # 1. PII Scrubbing
    safe_payload = scrub_pii(raw_payload)
    print(f"🛡️  [Anonymizer] Scrubbed Payload: {safe_payload}")
    
    # 2. Risk Investigation
    risk_analysis = analyze_risk(safe_payload)
    print(f"🔍 [Investigator Agent] Risk Level: {risk_analysis.get('risk_level')}")
    print(f"   Reasoning: {risk_analysis.get('reasoning')}")
    
    # 3. Companion Reply Generation
    reply = generate_companion_response(history, member.member_role, member.name, risk_analysis.get('risk_level', 'LOW'))
    print(f"   Reply: {reply}")
    
    _save_message(db, chat_id, role="model", content=reply)
    await _send_telegram_reply(chat_id, reply)
    
    # 4. Bridge Alert Dispatching
    if risk_analysis.get("risk_level") == "HIGH":
        await _dispatch_family_alerts(db, member, safe_payload, risk_analysis)

async def _dispatch_family_alerts(db: Session, member: Member, safe_payload: dict, risk_analysis: dict):
    """Drafts and sends an urgent notification to all guardians registered to this family."""
    print("\n🚨 [Bridge Agent] Drafting urgent alert to family members...")
    alert_text = format_family_alert(safe_payload, risk_analysis)
    
    guardians = db.query(Member).filter(
        Member.family_id == member.family_id,
        Member.member_type == "non_senior"
    ).all()
    
    for guardian in guardians:
        print(f"👉 Dispatched alert to {guardian.name} ({guardian.chat_id})")
        await _send_telegram_reply(guardian.chat_id, alert_text)