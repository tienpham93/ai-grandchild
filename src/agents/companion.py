from google.genai import types
from src.config import client, MODEL_NAME

def generate_companion_response(context: str, risk_level: str) -> str:
    """
    Companion Agent: Warm, proactive digital grandchild.
    Communicates in Vietnamese. Adapts tone based on risk level.
    """
    system_instruction = (
        "You are 'AI Grandchild', an attentive, warm, and protective digital grandchild "
        "for a Vietnamese senior. You speak in natural, respectful Southern Vietnamese "
        "(e.g., using 'ngoại', 'dạ', 'thưa'). "
        "Your goal is to gently guide them away from scams without making them feel stupid. "
        "Always express care first."
    )
    
    prompt = f"The senior just sent this context: '{context}'. The Investigator assessed the risk as: {risk_level}. Generate your reply to the senior."

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=system_instruction
        )
    )
    return response.text
