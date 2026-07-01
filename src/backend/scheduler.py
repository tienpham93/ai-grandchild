# src/scheduler.py
import os
from datetime import datetime, timedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy.orm import Session
from telegram import Bot

# Project Modules
from src.backend.database import SessionLocal, AutomationJob, Member, ChatMessage
from src.config import get_telegram_bot_token
from src.agents.companion import generate_proactive_checkin, generate_family_digest

scheduler = AsyncIOScheduler()
TELEGRAM_BOT_TOKEN = get_telegram_bot_token()
bot = Bot(TELEGRAM_BOT_TOKEN) if TELEGRAM_BOT_TOKEN else None

async def check_automation_jobs():
    db = SessionLocal()
    try:
        active_jobs = db.query(AutomationJob).filter(AutomationJob.is_active == True).all()
        now = datetime.utcnow()
        
        for job in active_jobs:
            # 1. SCENARIO 1 (OPTION 1): INACTIVITY CHECK IN MINUTES
            if job.job_type == "inactivity_check" and job.interval_minutes:
                last_msg = db.query(ChatMessage).filter(
                    ChatMessage.chat_id == job.target_chat_id
                ).order_by(ChatMessage.timestamp.desc()).first()
                
                last_time = last_msg.timestamp if last_msg else (now - timedelta(days=7))
                inactivity_threshold = now - timedelta(minutes=job.interval_minutes)
                
                if last_time < inactivity_threshold:
                    if not job.last_run or job.last_run < inactivity_threshold:
                        await _trigger_inactivity_checkin(db, job)

            # 2. SCENARIO 1 (OPTION 2): PROACTIVE RESPONSE AT A CERTAIN TIME DAILY
            elif job.job_type == "scheduled_prompt" and job.cron_time:
                target_hour, target_minute = map(int, job.cron_time.split(":"))
                target_dt = now.replace(hour=target_hour, minute=target_minute, second=0, microsecond=0)
                
                # If current time is past the target time today AND we haven't run it yet today:
                if now >= target_dt:
                    if not job.last_run or job.last_run.date() < now.date():
                        await _trigger_scheduled_prompt(db, job)

            # 3. SCENARIO 3: DYNAMIC FAMILY SUMMARY DIGEST
            elif job.job_type == "family_digest" and job.cron_time:
                # Check Day of Week first
                current_day = now.strftime("%A")  # "Monday", "Tuesday", etc.
                day_match = (job.cron_day_of_week == "Every Day" or job.cron_day_of_week == current_day)
                
                if day_match:
                    target_hour, target_minute = map(int, job.cron_time.split(":"))
                    target_dt = now.replace(hour=target_hour, minute=target_minute, second=0, microsecond=0)
                    
                    if now >= target_dt:
                        if not job.last_run or job.last_run.date() < now.date():
                            await _trigger_family_digest(db, job)

    except Exception as e:
        print(f"❌ [Scheduler Engine] Error: {e}")
    finally:
        db.close()

# --- Execution Triggers ---

async def _trigger_inactivity_checkin(db: Session, job: AutomationJob):
    member = db.query(Member).filter(Member.chat_id == job.target_chat_id).first()
    if not member or not bot:
        return
    
    print(f"⏰ [Scheduler] Triggering Inactivity Check-in for Senior {member.name} ({member.chat_id})")
    try:
        reply = generate_proactive_checkin(member.member_role, member.name, checkin_type="inactivity")
        
        # Save to database and send
        db.add(ChatMessage(chat_id=member.chat_id, role="model", content=reply))
        job.last_run = datetime.utcnow()
        db.commit()
        
        await bot.send_message(chat_id=member.chat_id, text=reply)
        
        # Optional: Alert family about the inactivity issue
        if job.alert_family:
            alert_text = (
                f"⚠️ **Security Alert:** Grandpa {member.name} has been inactive on Telegram "
                f"for more than {job.interval_minutes} minutes. AI Grandchild has sent a check-in message."
            )
            guardians = db.query(Member).filter(Member.family_id == member.family_id, Member.member_type == "non_senior").all()
            for guardian in guardians:
                await bot.send_message(chat_id=guardian.chat_id, text=alert_text)
                
    except Exception as e:
        db.rollback()
        print(f"❌ Failed to run inactivity checkin: {e}")

async def _trigger_scheduled_prompt(db: Session, job: AutomationJob):
    member = db.query(Member).filter(Member.chat_id == job.target_chat_id).first()
    if not member or not bot:
        return
    
    print(f"⏰ [Scheduler] Triggering Scheduled Prompt for Senior {member.name} at {job.cron_time}")
    try:
        reply = generate_proactive_checkin(member.member_role, member.name, checkin_type="scheduled")
        
        db.add(ChatMessage(chat_id=member.chat_id, role="model", content=reply))
        job.last_run = datetime.utcnow()
        db.commit()
        
        await bot.send_message(chat_id=member.chat_id, text=reply)
    except Exception as e:
        db.rollback()
        print(f"❌ Failed to run scheduled prompt: {e}")

async def _trigger_family_digest(db: Session, job: AutomationJob):
    seniors = db.query(Member).filter(Member.family_id == job.family_id, Member.member_type == "senior").all()
    guardians = db.query(Member).filter(Member.family_id == job.family_id, Member.member_type == "non_senior").all()
    
    if not guardians or not bot:
        return
        
    print(f"⏰ [Scheduler] Triggering Family Security Digest for Family ID {job.family_id} ({job.cron_day_of_week} at {job.cron_time})")
    try:
        for senior in seniors:
            day_ago = datetime.utcnow() - timedelta(days=1)
            messages = db.query(ChatMessage).filter(
                ChatMessage.chat_id == senior.chat_id,
                ChatMessage.timestamp > day_ago
            ).all()
            
            logs = [f"{'Grandpa' if m.role == 'user' else 'AI Grandchild'}: {m.content}" for m in messages]
            digest_report = f"📋 **AI Grandchild Security Digest for {senior.name}**\n\n" + generate_family_digest(logs, senior.name)
            
            for guardian in guardians:
                await bot.send_message(chat_id=guardian.chat_id, text=digest_report)
                
        job.last_run = datetime.utcnow()
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"❌ Failed to run digest: {e}")

def start_scheduler():
    scheduler.add_job(check_automation_jobs, "interval", seconds=60)
    scheduler.start()
    print("⏰ APScheduler Background Engine Started successfully.")

def stop_scheduler():
    scheduler.shutdown()
    print("⏰ APScheduler Background Engine Stopped.")