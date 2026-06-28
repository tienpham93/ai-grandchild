import json
from google.genai import types
from src.config import get_gemini_client

def format_family_alert(event: dict, risk_analysis: dict) -> str:
    """
    Bridge Agent: Formats secure, actionable alerts for family members.
    Only triggered if risk is HIGH.
    """
    if risk_analysis.get("risk_level") != "HIGH":
        return "No alert necessary."
        
    client = get_gemini_client()
    
    system_instruction = (
        "Bạn là Bridge Agent. Công việc của bạn là soạn thảo một tin nhắn SMS khẩn cấp nhưng rõ ràng "
        "gửi cho một thành viên trong gia đình về một vụ lừa đảo tiềm năng nhắm vào người thân cao tuổi của họ. "
        "Hãy cô đọng, nêu rõ rủi ro và đề xuất một hành động ngay lập tức."
    )
    
    prompt = f"Chi tiết sự kiện: {json.dumps(event, ensure_ascii=False)}\nPhân tích rủi ro: {json.dumps(risk_analysis, ensure_ascii=False)}\nSoạn thảo tin nhắn SMS cảnh báo."

    response = client.models.generate_content(
        model='gemini-3.5-flash',
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=system_instruction
        )
    )
    return response.text