.PHONY: init run tunnel clean

init:
	@echo "Initializing uv environment and installing dependencies..."
	uv sync

run:
	@echo "Starting AI Grandchild FastAPI server on port 8000..."
	uv run uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload

tunnel:
	@echo "Starting localtunnel -> https://ai-grandchild-vn.loca.lt"
	npx --yes localtunnel --port 8000 --local-host localhost --subdomain ai-grandchild-vn

clean:
	@echo "Cleaning up environment..."
	rm -rf .venv
	rm -rf .uv
	find . -type d -name __pycache__ -exec rm -rf {} +
