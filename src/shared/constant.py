import os


BACKEND_URL = os.environ.get("BACKEND_URL", "http://backend:8000")

LOCALE = os.environ.get("LOCALE")
DATABASE_URL = os.environ.get("DATABASE_URL", f"sqlite:///./data/ai_grandchild_{LOCALE}.db")