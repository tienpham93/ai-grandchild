from fastapi import APIRouter, HTTPException, Depends
from requests import Session
from src.backend.database import AgentConfig, get_db 

router = APIRouter()

@router.get("/api/agents")
def list_agents(db: Session = Depends(get_db)):
    return db.query(AgentConfig).all()

@router.put("/api/agents/{agent_id}")
def update_agent(agent_id: str, data: dict, db: Session = Depends(get_db)):
    agent = db.query(AgentConfig).filter(AgentConfig.id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent configuration not found")
    
    agent.system_prompt = data.get("system_prompt", agent.system_prompt)
    agent.goal = data.get("goal", agent.goal)
    
    try:
        db.commit()
        db.refresh(agent)
        return agent
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Failed to update agent configuration: {e}")