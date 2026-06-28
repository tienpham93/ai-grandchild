.PHONY: init up down restart logs run server tunnel dashboard set-telegram-webhook clean

# System Configurations
APP_PORT = 8000
SUBDOMAIN = ai-grandchild-vn

# --- 📦 Initialization ---
init:
	@echo "Initializing uv environment and installing dependencies..."
	uv sync

# --- 🐳 Docker Container Management ---
up:
	@echo "Building and starting containers in background..."
	docker compose up --build -d

down:
	@echo "Stopping all active containers..."
	docker compose down

restart:
	@echo "Restarting containers..."
	docker compose restart

logs:
	@echo "Streaming execution logs..."
	docker compose logs -f

# --- 💻 Local Development (Non-Containerized) ---
run:
	@echo "Starting local CLI mock simulation..."
	uv run python src/main.py

server:
	@echo "Starting FastAPI server on port $(APP_PORT)..."
	uv run uvicorn src.main:app --host 0.0.0.0 --port $(APP_PORT) --reload

dashboard:
	@echo "Starting Streamlit administration dashboard..."
	uv run streamlit run src/dashboard.py

tunnel:
	@echo "Starting localtunnel -> https://$(SUBDOMAIN).loca.lt"
	npx --yes localtunnel --port $(APP_PORT) --local-host localhost --subdomain $(SUBDOMAIN) --set-headers "bypass-tunnel-remind: true"

# --- 🔌 Integration & Testing ---
set-telegram-webhook:
	@echo "Registering webhook URL with Telegram API..."
	uv run python -c "import requests, os; from dotenv import load_dotenv; load_dotenv(); token = os.environ.get('TELEGRAM_BOT_TOKEN'); url = f'https://api.telegram.org/bot{token}/setWebhook?url=https://$(SUBDOMAIN).loca.lt/telegram-webhook'; print(f'Requesting: {url}'); response = requests.get(url); print(f'Telegram API Response: {response.json()}')"

# --- 🧹 Cleanup ---
clean:
	@echo "Cleaning environment artifacts..."
	rm -rf .venv
	rm -rf .uv
	rm -f requirements.txt
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# Runs the CLI loop locally for mock simulations & seeding
run:
	@echo "Starting local CLI mock simulation and database seeding..."
	uv run python src/seeding.py