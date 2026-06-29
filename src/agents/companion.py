from google.genai import types
from src.config import get_gemini_client
from src.backend.database import SessionLocal, AgentConfig # Use session to read config

def generate_companion_response(history: list[dict], role: str, name: str, risk_level: str) -> str:
    client = get_gemini_client()

    db = SessionLocal()
    try:
        agent_cfg = db.query(AgentConfig).filter(AgentConfig.id == "companion").first()
        base_instruction = agent_cfg.system_prompt if agent_cfg else "Default companion prompt fallback"
    finally:
        db.close()

    system_instruction = (
        f"{base_instruction}\n"
        f"Bạn đang nói chuyện trực tiếp với: {name} (Vai trò: {role}). Hãy xưng hô đúng vai vế."
    )

    history_text = ""
    for msg in history[:-1]:
        label = "Cháu" if msg["role"] == "model" else role.capitalize()
        history_text += f"{label}: {msg['content']}\n"

    latest_msg = history[-1]["content"] if history else ""

    prompt = (
        f"Lịch sử cuộc trò chuyện trước đó:\n{history_text}\n"
        f"Tin nhắn mới nhất từ {role} ({name}): '{latest_msg}'\n"
        f"Mức độ rủi ro hiện tại: {risk_level}.\n"
        "Hãy viết tin nhắn trả lời trực tiếp gửi cho họ."
    )

    response = client.models.generate_content(
        model='gemini-3.5-flash',
        contents=prompt,
        config=types.GenerateContentConfig(system_instruction=system_instruction)
    )
    return response.text

def generate_family_response(history: list[dict], role: str, name: str) -> str:
    client = get_gemini_client()

    # Reusing the base companion profile for family system structures
    db = SessionLocal()
    try:
        agent_cfg = db.query(AgentConfig).filter(AgentConfig.id == "companion").first()
        base_instruction = agent_cfg.system_prompt if agent_cfg else "Default assistant prompt fallback"
    finally:
        db.close()

    system_instruction = (
        f"{base_instruction}\n\n"
        "Bối cảnh hiện tại:\n"
        "Bạn đang nói chuyện với một người nhà (bố mẹ hoặc con cháu của người lớn tuổi) "
        f"tên là: {name} (Vai trò: {role}).\n"
        "Mục tiêu của bạn lúc này là đóng vai trò như một trợ lý bảo mật gia đình thông minh. "
        "Hãy báo cáo, cập nhật tình hình của ông bà một cách lễ phép, lịch sự, rõ ràng bằng tiếng Việt."
    )

    history_text = ""
    for msg in history[:-1]:
        label = "Trợ lý" if msg["role"] == "model" else role.capitalize()
        history_text += f"{label}: {msg['content']}\n"

    latest_msg = history[-1]["content"] if history else ""

    prompt = (
        f"Lịch sử cuộc trò chuyện trước đó:\n{history_text}\n"
        f"Tin nhắn mới nhất từ {role}: '{latest_msg}'\n"
        "Hãy viết tin nhắn trả lời phản hồi cho họ."
    )

    response = client.models.generate_content(
        model='gemini-3.5-flash',
        contents=prompt,
        config=types.GenerateContentConfig(system_instruction=system_instruction)
    )
    return response.text