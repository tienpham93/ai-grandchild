import json
from google.genai import types
from src.config import get_gemini_client
from src.backend.database import SessionLocal, AgentConfig # Use session to read config
from src.agents.skills.behavioral_search import search_known_scam_behaviors

def analyze_risk(event: dict) -> dict:
    client = get_gemini_client()

    # Query system instruction from Database
    db = SessionLocal()
    try:
        agent_cfg = db.query(AgentConfig).filter(AgentConfig.id == "investigator").first()
        system_instruction = agent_cfg.system_prompt if agent_cfg else "Default analyzer prompt fallback"
    finally:
        db.close()

    tool_context = []
    event_str = json.dumps(event, ensure_ascii=False)
        
    behavior_search_results = search_known_scam_behaviors(event_str)
    if behavior_search_results:
        tool_context.append(f"Output searh behavior: {behavior_search_results}")
    
    prompt_parts = [f"Events need to analyze: {event_str}"]
    if tool_context:
        prompt_parts.append("\n".join(tool_context))

    prompt_content = "\n\n".join(prompt_parts)

    response = client.models.generate_content(
        model='gemini-3.5-flash',
        contents=prompt_content,
        config=types.GenerateContentConfig(
            system_instruction=system_instruction,
            response_mime_type="application/json"
        )
    )
    
    try:
        response_text = response.text.strip()
        if response_text.startswith("```json") and response_text.endswith("```"):
            response_text = response_text[7:-3].strip()
        return json.loads(response_text)
    except Exception as e:
        print(f"Error parsing LLM output to JSON: {response.text} - Error: {e}")
        return {"risk_level": "UNKNOWN", "reasoning": f"Failed to parse LLM output: {e}"}