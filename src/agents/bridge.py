import json
from google.genai import types
from src.config import get_gemini_client
from src.backend.database import SessionLocal, AgentConfig # Use session to read config

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
    
    prompt = f"Chi tiết sự kiện: {json.dumps(event, ensure_ascii=False)}\nPhân tích rủi ro: {json.dumps(risk_analysis, ensure_ascii=False)}\nSoạn thảo tin nhắn SMS cảnh báo."

    response = client.models.generate_content(
        model='gemini-3.5-flash',
        contents=prompt,
        config=types.GenerateContentConfig(system_instruction=system_instruction)
    )
    return response.text