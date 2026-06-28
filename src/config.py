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
    return os.environ.get("TELEGRAM_BOT_TOKEN")