# src/config.py
import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

_client = None

def init_gemini():
    """Verifies the API key and initializes the Gemini Client."""
    global _client
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("❌ ERROR: GEMINI_API_KEY environment variable not set.")
        print("Please set it in your .env file or environment.")
        exit(1)
    
    _client = genai.Client(api_key=api_key)
    print("✅ Gemini Client successfully initialized using google-genai.")

def get_gemini_client():
    """Returns the initialized Gemini Client instance."""
    global _client
    if _client is None:
        init_gemini()
    return _client

def get_telegram_bot_token() -> str | None:
    """Returns the Telegram bot token from environment variables."""
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not token:
        print("⚠️ TELEGRAM_BOT_TOKEN environment variable not set.")
    return token

# --- Dynamic ID List Getters ---
def get_family_chat_ids() -> set[str]:
    """Returns a set of authorized Family Member chat IDs from .env."""
    load_dotenv()
    ids_str = os.environ.get("FAMILY_CHAT_IDS", "")
    return {uid.strip() for uid in ids_str.split(",") if uid.strip()}

def get_senior_chat_ids() -> set[str]:
    """Returns a set of authorized Senior (Grandpa) chat IDs from .env."""
    load_dotenv()
    ids_str = os.environ.get("SENIOR_CHAT_IDS", "")
    return {uid.strip() for uid in ids_str.split(",") if uid.strip()}