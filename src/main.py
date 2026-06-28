# src/main.py
import os
import json
import asyncio
from fastapi import FastAPI, BackgroundTasks, Request, Response, HTTPException
from fastapi.responses import FileResponse
from dotenv import load_dotenv
from telegram import Bot
from telegram.error import TelegramError

# Load environment variables
load_dotenv()

# Project Modules
from src.config import init_gemini, get_telegram_bot_token, get_family_chat_ids, get_senior_chat_ids
from src.skills.anonymizer import scrub_pii
from src.agents.investigator import analyze_risk
from src.agents.companion import generate_companion_response, generate_family_response
from src.agents.bridge import format_family_alert

# Initialize Gemini Client connection on startup
init_gemini()

# Initialize Telegram Bot
TELEGRAM_BOT_TOKEN = get_telegram_bot_token()
if TELEGRAM_BOT_TOKEN:
    bot = Bot(TELEGRAM_BOT_TOKEN)
else:
    bot = None
    print("⚠️ Telegram Bot Token not found. Live replies will be disabled.")

app = FastAPI(title="AI Grandchild - Webhook Server")

# --- In-Memory Thread Storage ---
# Maps chat_id -> list of message dicts: [{"role": "user"|"model", "content": "..."}]
CONVERSATION_HISTORY = {}

async def process_chat_event(json_payload: dict, chat_id: str | None = None):
    """
    Runs the background agent pipeline with dedicated user roles and conversation memory.
    """
    family_ids = get_family_chat_ids()
    senior_ids = get_senior_chat_ids()
    user_message_text = json_payload.get("message_text", "")

    # Initialize history list for this chat_id if not present
    if chat_id not in CONVERSATION_HISTORY:
        CONVERSATION_HISTORY[chat_id] = []

    # Store the incoming message
    CONVERSATION_HISTORY[chat_id].append({"role": "user", "content": user_message_text})
    # Limit context size to prevent context window bloat (keep last 10 messages)
    CONVERSATION_HISTORY[chat_id] = CONVERSATION_HISTORY[chat_id][-10:]
    current_history = CONVERSATION_HISTORY[chat_id]

    # --- ROLE ROUTING FLOW ---
    
    # Flow A: Authorized Family Member
    if chat_id in family_ids:
        print("\n" + "="*60)
        print(f"👨‍👩‍👧‍👦 RECEIVED FAMILY CHAT EVENT from chat_id {chat_id}")
        print("💬 [Companion Agent] Generating reassuring reply with thread memory...")
        try:
            family_reply = generate_family_response(current_history)
            print(f"   Reply: {family_reply}")
            
            # Save the bot response into the thread memory
            CONVERSATION_HISTORY[chat_id].append({"role": "model", "content": family_reply})
            
            if bot:
                await bot.send_message(chat_id=chat_id, text=family_reply)
                print(f"✅ Sent family helper reply back to Telegram: {chat_id}")
        except Exception as e:
            print(f"❌ Family flow execution failed: {e}")
            
        print("="*60 + "\n")
        return

    # Flow B: Authorized Senior (Grandpa)
    elif chat_id in senior_ids:
        print("\n" + "="*60)
        print(f"📥 RECEIVED SENIOR CHAT EVENT from chat_id {chat_id}")
        
        # 1. Anonymize PII (CCCD, Bank Accounts)
        safe_payload = scrub_pii(json_payload)
        print(f"🛡️  [Anonymizer] Scrubbed Payload: {safe_payload}")
        
        # 2. Investigator Analysis (Cynical Backend Analyzer)
        print("\n🔍 [Investigator Agent] Analyzing...")
        try:
            risk_analysis = analyze_risk(safe_payload) 
            print(f"   Risk Level: {risk_analysis.get('risk_level')}")
            print(f"   Reasoning: {risk_analysis.get('reasoning')}")
            
            # 3. Companion Response (Using thread-specific memory)
            print("\n💬 [Companion Agent] Generating context-aware reply...")
            companion_reply = generate_companion_response(
                history=current_history, 
                risk_level=risk_analysis.get('risk_level', 'UNKNOWN')
            )
            print(f"   Reply: {companion_reply}")

            # Save the bot response into the thread memory
            CONVERSATION_HISTORY[chat_id].append({"role": "model", "content": companion_reply})

            # Send reply back to the Telegram chat of the Senior
            if bot:
                try:
                    await bot.send_message(chat_id=chat_id, text=companion_reply)
                    print(f"✅ Sent reply back to Telegram chat: {chat_id}")
                except TelegramError as e:
                    print(f"❌ Failed to send Telegram reply: {e}")
            
            # 4. Bridge Alert (Sends notification to ALL configured family members)
            if risk_analysis.get('risk_level') == "HIGH":
                print("\n🚨 [Bridge Agent] Drafting family alert...")
                family_alert = format_family_alert(safe_payload, risk_analysis)
                print(f"   Alert: {family_alert}")
                
                # Broad-cast alert notification to all registered family members
                for family_id in family_ids:
                    if bot:
                        try:
                            await bot.send_message(chat_id=family_id, text=family_alert)
                            print(f"✅ Sent family alert to Telegram chat_id: {family_id}")
                        except TelegramError as e:
                            print(f"❌ Failed to send family alert to chat_id {family_id}: {e}")
                
        except Exception as e:
            print(f"❌ Pipeline failed: {e}")
            
        print("="*60 + "\n")
        return

    # Fallback/Safety block: User not in allowed list
    else:
        print(f"🚫 IGNORED unauthorized message from chat_id: {chat_id}")

@app.post("/telegram-webhook")
async def handle_telegram_webhook(request: Request, background_tasks: BackgroundTasks):
    try:
        update = await request.json()
        message = update.get('message')
        if not message:
            return {"status": "ignored", "message": "No message in update"}

        chat_id = str(message['chat']['id'])
        
        # Check overall whitelist
        allowed_ids_str = os.environ.get("ALLOWED_CHAT_IDS", "")
        if allowed_ids_str:
            allowed_ids = {uid.strip() for uid in allowed_ids_str.split(",") if uid.strip()}
            if chat_id not in allowed_ids:
                print(f"🚫 IGNORED message from unauthorized chat_id: {chat_id}")
                return {"status": "ignored", "message": "Unauthorized user"}

        user_message_text = message.get('text')
        if not user_message_text:
            return {"status": "ignored", "message": "No text message"}
        
        payload_for_agents = {
            "event_name": "user_send_text",
            "sender_id": str(message['from']['id']),
            "message_text": user_message_text,
            "timestamp": message.get('date')
        }
        
        background_tasks.add_task(process_chat_event, payload_for_agents, chat_id)
        return {"status": "success", "message": "Event received and queued."}
    
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
def root():
    return {"status": "running", "message": "AI Grandchild Webhook Server is active."}

@app.get("/{filename}")
def serve_static_file(filename: str):
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    file_path = os.path.join(base_dir, "static", filename)
    if os.path.isfile(file_path):
        return FileResponse(file_path)
    return {"error": "File not found"}, 404

# --- CLI local Simulation Loop ---
if __name__ == "__main__":
    print("--- AI Grandchild CLI Simulation Started (using mock_inputs.json) ---")
    mock_data_path = os.path.join(os.path.dirname(__file__), "data", "mock_inputs.json")
    if not os.path.exists(mock_data_path):
        print(f"❌ Error: Mock data file not found at {mock_data_path}")
        exit(1)

    with open(mock_data_path, 'r', encoding='utf-8') as f:
        mock_inputs = json.load(f)

    for i, mock_payload in enumerate(mock_inputs):
        print(f"\n--- Processing Mock Scenario {i+1} ---")
        asyncio.run(process_chat_event(mock_payload, chat_id="7799435300")) # Simulate as Senior Grandpa
    
    print("\n--- AI Grandchild CLI Simulation Finished ---")