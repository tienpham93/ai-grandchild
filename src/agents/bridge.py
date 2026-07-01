# src/agents/bridge.py
import json
from google.genai import types
from src.config import get_gemini_client
from src.backend.database import SessionLocal, AgentConfig

def format_family_alert(event: dict, risk_analysis: dict) -> str:
    if risk_analysis.get("risk_level") != "HIGH":
        return "No alert necessary."
        
    client = get_gemini_client()

    db = SessionLocal()
    try:
        agent_cfg = db.query(AgentConfig).filter(AgentConfig.id == "bridge").first()
        system_instruction = agent_cfg.system_prompt if agent_cfg else "Default bridge prompt fallback"
    finally:
        db.close()
    
    prompt = (
        f"Event details: {json.dumps(event, ensure_ascii=False)}\n"
        f"Risk analysis: {json.dumps(risk_analysis, ensure_ascii=False)}\n"
        "Draft the English SMS alert."
    )

    response = client.models.generate_content(
        model='gemini-1.5-flash',
        contents=prompt,
        config=types.GenerateContentConfig(system_instruction=system_instruction)
    )
    return response.text