# src/agents/companion.py
from google.genai import types
from src.config import get_gemini_client
from src.backend.database import SessionLocal, AgentConfig

def generate_proactive_checkin(role: str, name: str, checkin_type: str = "inactivity") -> str:
    """
    Generates a proactive, caring conversation starter in Southern Vietnamese.
    Inactivity check-in Scenarios where it's been a long time No chat occurred.
    """
    client = get_gemini_client()
    
    context_desc = "it's been a while since I last heard from you" if checkin_type == "inactivity" else "I just wanted to check in and see how you are doing"
    
    prompt = (
        "You are 'AI Grandchild', a deeply loving, attentive grandchild checking in on your elderly relative.\n"
        f"You are proactively messaging to check in on: {name} ({role}) because {context_desc}.\n"
        "Speak in a natural, warm, affectionate, and respectful conversational English tone "
        "(using terms like 'grandma', 'grandpa', 'pops', 'sweetheart' naturally).\n"
        "Ask a warm, gentle, and lighthearted question about how they are doing to spark a friendly family conversation."
    )

    response = client.models.generate_content(
        model='gemini-3.5-flash',
        contents=prompt
    )
    return response.text

def generate_family_digest(history_logs: list[str], senior_name: str) -> str:
    """
    Companion Agent (Family Summary): Compiles and digests historical chats into a safety report.
    """
    client = get_gemini_client()
    
    logs_text = "\n".join(history_logs) if history_logs else "No messages exchanged in this period."
    
    prompt = (
        "You are 'AI Grandchild', an intelligent family security assistant helping families protect "
        "their elderly relatives from holiday and timeshare scams.\n"
        f"Please read the recent chat logs of: {senior_name} below and draft a concise, clear, and professional "
        "safety digest report in English to be sent to their family members.\n"
        "The report must include:\n"
        "1. Conversation Summary: What have they been chatting about (general mood, notable updates, etc.)?\n"
        "2. Safety Assessment: Is there any suspicious behavior, potential scam indicators, or security threats detected?\n"
        "3. Actionable Advice/Next Steps: Recommended actions for the family (if any).\n\n"
        f"Chat Logs:\n{logs_text}"
    )

    response = client.models.generate_content(
        model='gemini-3.5-flash',
        contents=prompt
    )
    return response.text

def generate_companion_response(history: list[dict], role: str, name: str, risk_level: str) -> str:
    """
    Companion Agent: Warm, proactive digital grandchild speaking in English.
    """
    client = get_gemini_client()

    db = SessionLocal()
    try:
        agent_cfg = db.query(AgentConfig).filter(AgentConfig.id == "companion").first()
        base_instruction = agent_cfg.system_prompt if agent_cfg else "You are 'AI Grandchild', a loving grandchild."
    finally:
        db.close()

    system_instruction = (
        f"{base_instruction}\n"
        f"You are currently talking directly to: {name} (Family Role: {role}). Adhere to this role relationship.\n"
        "Ensure your tone aligns with the assessed risk level:\n"
        "- LOW Risk: Ask warm questions, be lighthearted and supportive.\n"
        "- MEDIUM Risk: Express subtle, gentle concern, asking curious questions to uncover company details.\n"
        "- HIGH Risk: Express urgent, loving concern, urging them to halt actions and talk to you first."
    )

    history_text = ""
    for msg in history[:-1]:
        label = "Grandchild" if msg["role"] == "model" else role.capitalize()
        history_text += f"{label}: {msg['content']}\n"

    latest_msg = history[-1]["content"] if history else ""

    prompt = (
        f"Conversational History:\n{history_text}\n"
        f"Latest message from {role} ({name}): '{latest_msg}'\n"
        f"Investigator Risk Assessment: {risk_level}.\n"
        "Generate your direct reply to them."
    )

    response = client.models.generate_content(
        model='gemini-3.5-flash',
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=system_instruction
            )
    )
    return response.text

def generate_family_response(history: list[dict], role: str, name: str) -> str:
    """
    Companion Agent (Family Mode): Professional security assistant for family guardians.
    """
    client = get_gemini_client()
    db = SessionLocal()
    try:
        agent_cfg = db.query(AgentConfig).filter(AgentConfig.id == "companion").first()
        base_instruction = agent_cfg.system_prompt if agent_cfg else "Default assistant prompt fallback"
    finally:
        db.close()

    system_instruction = (
        f"{base_instruction}\n\n"
        "You are 'AI Grandchild', an intelligent family security assistant helping families protect "
        f"their elderly relatives from holiday and timeshare scams. You are talking to: {name} (Role: {role}).\n"
        "Keep your responses polite, professional, reassuring, and concise in English."
    )

    history_text = ""
    for msg in history[:-1]:
        label = "Assistant" if msg["role"] == "model" else role.capitalize()
        history_text += f"{label}: {msg['content']}\n"

    latest_msg = history[-1]["content"] if history else ""

    prompt = (
        f"Conversational History:\n{history_text}\n"
        f"Latest question from {role}: '{latest_msg}'\n"
        "Please generate your response."
    )

    response = client.models.generate_content(
        model='gemini-3.5-flash',
        contents=prompt,
        config=types.GenerateContentConfig(system_instruction=system_instruction)
    )
    return response.text