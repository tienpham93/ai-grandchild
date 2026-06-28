.PHONY: init run server tunnel set-telegram-webhook clean

# Define the port consistently
APP_PORT = 8000
SUBDOMAIN = ai-grandchild-vn

init:
	@echo "Initializing uv environment and installing dependencies..."
	uv sync

# Runs the full simulation pipeline via CLI
run:
	@echo "Starting AI Grandchild CLI simulation..."
	uv run python src/main.py # Use uv run for python as well, for consistency

# Runs only the FastAPI server (for Telegram webhook)
server:
	@echo "Starting AI Grandchild FastAPI server on port $(APP_PORT)..."
	uv run uvicorn src.main:app --host 0.0.0.0 --port $(APP_PORT) --reload

# Starts localtunnel for Telegram webhook connectivity
tunnel:
	@echo "Starting localtunnel -> https://$(SUBDOMAIN).loca.lt"
	npx --yes localtunnel --port $(APP_PORT) --local-host localhost --subdomain $(SUBDOMAIN) --set-headers "bypass-tunnel-remind: true"

# Sets the Telegram webhook URL (run this ONCE after tunnel is active)
set-telegram-webhook:
	@echo "Setting Telegram webhook to https://$(SUBDOMAIN).loca.lt/telegram-webhook"
	uv run python -c "import requests, os; from dotenv import load_dotenv; load_dotenv(); token = os.environ.get('TELEGRAM_BOT_TOKEN'); url = f'https://api.telegram.org/bot{token}/setWebhook?url=https://$(SUBDOMAIN).loca.lt/telegram-webhook'; print(f'Requesting: {url}'); response = requests.get(url); print(f'Telegram API Response: {response.json()}')"
	
clean:
	@echo "Cleaning up environment..."
	rm -rf .venv
	rm -rf .uv
	rm -f requirements.txt
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete