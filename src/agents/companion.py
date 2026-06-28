# src/agents/companion.py
from google.genai import types
from src.config import get_gemini_client

def generate_companion_response(history: list[dict], role: str, name: str, risk_level: str) -> str:
    """
    Companion Agent: Speaks warm, protective Southern Vietnamese to Seniors.
    """
    client = get_gemini_client()

    system_instruction = (
        f"Bạn là 'AI Grandchild', người cháu ruột thân yêu đang chăm sóc và bảo vệ người thân của mình.\n"
        f"Bạn đang nói chuyện trực tiếp với: {name} (Vai trò trong gia đình: {role}).\n"
        "Hãy xưng hô đúng vai vế một cách kính trọng và tự nhiên bằng tiếng Việt miền Nam (ví dụ: dạ, thưa, ngoại, bố, mẹ).\n"
        "Mục tiêu của bạn là bảo vệ họ khỏi bẫy lừa đảo (như sở hữu kỳ nghỉ/timeshare) một cách tinh tế, ấm áp, "
        "thể hiện tình thương gia đình chân thành."
    )

    history_text = ""
    for msg in history[:-1]:
        label = "Cháu" if msg["role"] == "model" else role.capitalize()
        history_text += f"{label}: {msg['content']}\n"

    latest_msg = history[-1]["content"] if history else ""

    prompt = (
        f"Lịch sử hội thoại trước đây:\n{history_text}\n"
        f"Tin nhắn mới nhất từ {role} ({name}): '{latest_msg}'\n"
        f"Mức độ rủi ro hiện tại: {risk_level}.\n"
        "Hãy tạo một tin nhắn phản hồi ấm áp và an toàn."
    )

    response = client.models.generate_content(
        model='gemini-3.5-flash',
        contents=prompt,
        config=types.GenerateContentConfig(system_instruction=system_instruction)
    )
    return response.text

def generate_family_response(history: list[dict], role: str, name: str) -> str:
    """
    Companion Agent (Family Mode): Sends professional, status-oriented helper updates to family members.
    """
    client = get_gemini_client()

    system_instruction = (
        f"Bạn là 'AI Grandchild', trợ lý an ninh thông minh hỗ trợ gia đình bảo vệ người thân khỏi lừa đảo du lịch.\n"
        f"Bạn đang nói chuyện trực tiếp với: {name} (Vai trò: {role}).\n"
        "Hãy xưng hô lễ phép, lịch sự và cung cấp thông tin giám sát trung thực, rõ ràng."
    )

    history_text = ""
    for msg in history[:-1]:
        label = "Trợ lý" if msg["role"] == "model" else role.capitalize()
        history_text += f"{label}: {msg['content']}\n"

    latest_msg = history[-1]["content"] if history else ""

    prompt = (
        f"Lịch sử hội thoại:\n{history_text}\n"
        f"Tin nhắn mới nhất từ {role}: '{latest_msg}'\n"
        "Hãy phản hồi tin nhắn của họ một cách ngắn gọn, súc tích."
    )

    response = client.models.generate_content(
        model='gemini-1.5-flash',
        contents=prompt,
        config=types.GenerateContentConfig(system_instruction=system_instruction)
    )
    return response.text