from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.backend.routes import adminService, schedulerService, agentService, accountService, webhook
from src.backend.database import init_db
from contextlib import asynccontextmanager
from src.backend.scheduler import start_scheduler, stop_scheduler

init_db()

# FastAPI Lifespan Handler
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup Events
    start_scheduler()
    yield
    # Shutdown Events
    stop_scheduler()

app = FastAPI(title="AI Grandchild - Decoupled Architecture Server", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Sub-routers
app.include_router(schedulerService.router)
app.include_router(adminService.router)
app.include_router(accountService.router)
app.include_router(agentService.router)
app.include_router(webhook.router)

# --- CLI Local Simulation Support ---
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)