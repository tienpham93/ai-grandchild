from google.genai import types
from src.config import client, MODEL_NAME

def format_family_alert(event: dict, risk_analysis: dict) -> str:
    """
    Bridge Agent: Formats secure, actionable alerts for family members.
    Only triggered if risk is HIGH.
    """
    if risk_analysis.get("risk_level") != "HIGH":
        return "No alert necessary."
        
    system_instruction = (
        "You are the Bridge Agent. Your job is to draft an urgent but clear SMS alert "
        "to a family member about a potential scam targeting their elderly relative. "
        "Be concise, state the risk clearly, and suggest an immediate action."
    )
    
    prompt = f"Event Details: {event}\nRisk Analysis: {risk_analysis}\nDraft the SMS alert."

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=system_instruction
        )
    )
    return response.text
