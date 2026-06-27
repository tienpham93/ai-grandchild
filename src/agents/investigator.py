import json
from google.genai import types
from src.config import client, MODEL_NAME
from src.skills.geofencing import verify_high_risk_location
from src.skills.behavioral_search import search_known_scam_behaviors

def analyze_risk(event: dict) -> dict:
    """
    Investigator Agent: Cynical back-end fraud pattern analysis.
    Uses skills to determine if the event is a scam.
    """
    system_instruction = (
        "You are the Investigator Agent. You are cynical and highly trained in detecting "
        "Vietnamese timeshare and vacation contract scams (like the 2.7T VND ring). "
        "Analyze the provided event and tool outputs. Return a JSON response with: "
        "'risk_level' (LOW, MEDIUM, HIGH) and 'reasoning' (brief explanation)."
    )
    
    # Run tools locally to gather context
    tool_context = ""
    event_str = json.dumps(event, ensure_ascii=False)
    
    if event.get("event_name") == "user_send_location":
        is_risky = verify_high_risk_location(
            event.get("address", ""), 
            event.get("latitude", ""), 
            event.get("longitude", "")
        )
        tool_context += f"Geofencing Output: High-risk venue = {is_risky}\n"
        
    behavior_search = search_known_scam_behaviors(event_str)
    tool_context += f"Behavior Search Output: {behavior_search}\n"
    
    prompt = (
        f"Analyze this event: {event_str}\n"
        f"Tool Context:\n{tool_context}"
    )

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=system_instruction,
            response_mime_type="application/json"
        )
    )
    
    try:
        return json.loads(response.text)
    except Exception as e:
        return {"risk_level": "UNKNOWN", "reasoning": f"Failed to parse LLM output: {e}"}
