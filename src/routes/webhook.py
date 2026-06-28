# src/routes/webhook.py
import json
import time
from fastapi import APIRouter, BackgroundTasks, Request, HTTPException, Depends
from sqlalchemy.orm import Session

# Project Modules
from src.database import get_db, Member
from src.pipeline import process_chat_event

router = APIRouter()

# --- Live Telegram Webhook ---
@router.post("/telegram-webhook")
async def handle_telegram_webhook(request: Request, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    try:
        update = await request.json()
        message = update.get('message')
        if not message:
            return {"status": "ignored", "reason": "No message object"}

        chat_id = str(message['chat']['id'])
        
        member_exists = db.query(Member).filter(Member.chat_id == chat_id).first()
        if not member_exists:
            print(f"🚫 BLOCKED unauthorized webhook request from chat_id: {chat_id}")
            return {"status": "ignored", "reason": "Unregistered Chat ID"}

        user_message_text = message.get('text')
        if not user_message_text:
            return {"status": "ignored", "reason": "Empty or non-text message"}
        
        payload = {
            "event_name": "user_send_text",
            "sender_id": chat_id,
            "message_text": user_message_text,
            "timestamp": message.get('date')
        }
        
        background_tasks.add_task(process_chat_event, payload, chat_id)
        return {"status": "success"}
        
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")
    except Exception as e:
        print(f"❌ [Webhook Router] Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# --- NEW: Postman Simulator Endpoint for Bank SMS Webhooks ---
@router.post("/test/bank_sms_webhook")
async def simulate_bank_sms(data: dict, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """
    Simulates an incoming Bank transaction notification using realistic bank parameters.
    """
    bank_app_id = data.get("bank_app_id")
    bank_account = str(data.get("bank_account", ""))
    transaction_id = data.get("transaction_id")
    sms_content = data.get("sms_content", "")
    
    if not bank_account or not sms_content:
        raise HTTPException(status_code=400, detail="Missing bank_account or sms_content")
        
    # Dynamically resolve who this bank account belongs to via SQLite Query
    member = db.query(Member).filter(Member.bank_account == bank_account).first()
    if not member:
        raise HTTPException(
            status_code=404, 
            detail=f"Bank account {bank_account} is not linked to any registered family member."
        )
        
    payload = {
        "event_name": "bank_sms_webhook",
        "sender_id": member.chat_id, # Uses resolved Telegram chat ID
        "message_text": sms_content, # Evaluated through anonymizer and investigator
        "timestamp": int(time.time()),
        "bank_app_id": bank_app_id,
        "transaction_id": transaction_id
    }
    
    background_tasks.add_task(process_chat_event, payload, member.chat_id)
    return {
        "status": "success", 
        "message": f"Simulated transaction for {member.name} ({member.member_role}) resolved to chat_id {member.chat_id}"
    }