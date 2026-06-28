# src/agents/companion.py
from google.genai import types
from src.config import get_gemini_client

def generate_companion_response(history: list[dict], risk_level: str) -> str:
    """
    Companion Agent: Warm, proactive digital grandchild.
    Communicates in Southern Vietnamese. Maintains threat-aware memory of conversation.
    """
    client = get_gemini_client()

    system_instruction = (
        "Bạn là 'AI Grandchild', một người cháu kỹ thuật số chu đáo, ấm áp và bảo vệ "
        "dành cho người cao tuổi Việt Nam. Bạn nói bằng giọng miền Nam tự nhiên, kính trọng "
        "(ví dụ: dùng 'ngoại', 'dạ', 'thưa'). "
        "Mục tiêu của bạn là nhẹ nhàng hướng dẫn họ tránh xa các vụ lừa đảo mà không khiến họ cảm thấy bị coi thường. "
        "Dựa vào lịch sử hội thoại trước đó để trả lời tự nhiên, trôi chảy và nhất quán. "
        "Luôn thể hiện sự quan tâm trước tiên."
    )

    # Format the memory into a conversation log for the prompt
    history_text = ""
    for msg in history[:-1]:  # Exclude the latest user message to format it explicitly below
        role_label = "Cháu" if msg["role"] == "model" else "Ngoại"
        history_text += f"{role_label}: {msg['content']}\n"

    latest_msg = history[-1]["content"] if history else ""

    prompt = (
        f"Lịch sử cuộc trò chuyện trước đó:\n{history_text}\n"
        f"Ngoại vừa gửi tin nhắn mới nhất: '{latest_msg}'\n"
        f"Mức độ rủi ro hiện tại do Điều tra viên phân tích là: {risk_level}.\n"
        "Hãy viết tin nhắn trả lời trực tiếp gửi cho ngoại."
    )

    response = client.models.generate_content(
        model='gemini-3.5-flash',
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=system_instruction
        )
    )
    return response.text

def generate_family_response(history: list[dict]) -> str:
    """
    Companion Agent (Family Mode): Professional, reassuring helper for parents/children.
    Identifies context changes to answer questions accurately.
    """
    client = get_gemini_client()

    system_instruction = (
        "Bạn là 'AI Grandchild', trợ lý bảo mật thông minh giúp gia đình giám sát và bảo vệ ông bà "
        "khỏi các bẫy lừa đảo hợp đồng kỳ nghỉ (timeshare). Bạn đang nói chuyện với người nhà "
        "(bố mẹ hoặc con cháu của người lớn tuổi). "
        "Hãy trả lời một cách lễ phép, lịch sự, rõ ràng bằng tiếng Việt. "
        "Dựa trên lịch sử trò chuyện được cung cấp để trả lời chính xác, tránh lặp lại hoặc trả lời lạc đề."
    )

    # Format family history
    history_text = ""
    for msg in history[:-1]:
        role_label = "Trợ lý" if msg["role"] == "model" else "Người nhà"
        history_text += f"{role_label}: {msg['content']}\n"

    latest_msg = history[-1]["content"] if history else ""

    prompt = (
        f"Lịch sử cuộc trò chuyện trước đó:\n{history_text}\n"
        f"Người nhà vừa hỏi: '{latest_msg}'\n"
        "Hãy viết tin nhắn trả lời phản hồi cho họ."
    )

    response = client.models.generate_content(
        model='gemini-3.5-flash',
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=system_instruction
        )
    )
    return response.text