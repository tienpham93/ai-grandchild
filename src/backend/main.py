from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Initialize Database Schemes
from src.backend.routes import admin
from src.backend.routes import webhook
from src.database import init_db

init_db()

app = FastAPI(title="AI Grandchild - Decoupled Architecture Server")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Sub-routers
app.include_router(admin.router)
app.include_router(webhook.router)

# --- CLI Local Simulation Support ---
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)