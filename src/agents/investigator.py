import json
from google.genai import types
from src.config import get_gemini_client
from src.skills.geofencing import verify_high_risk_location
from src.skills.behavioral_search import search_known_scam_behaviors

def analyze_risk(event: dict) -> dict:
    """
    Investigator Agent: Cynical back-end fraud pattern analysis.
    Uses skills to determine if the event is a scam.
    """
    
    client = get_gemini_client()

    tool_context = []
    event_str = json.dumps(event, ensure_ascii=False)
    
    if event.get("event_name") == "user_send_location" or "address" in event:
        address = event.get("address", "")
        latitude = event.get("latitude", "")
        longitude = event.get("longitude", "")
        if address:
            is_risky_location = verify_high_risk_location(address, latitude, longitude)
            tool_context.append(f"Output Công cụ Geofencing: Địa điểm rủi ro cao = {is_risky_location}")
        
    behavior_search_results = search_known_scam_behaviors(event_str)
    if behavior_search_results:
        tool_context.append(f"Output Tìm kiếm Hành vi: {behavior_search_results}")
    
    system_instruction = (
        "Bạn là Điều tra viên. Bạn hoài nghi và được đào tạo chuyên sâu trong việc phát hiện "
        "các vụ lừa đảo du lịch và hợp đồng nghỉ dưỡng (ví dụ: đường dây 2.7 nghìn tỷ VND) tại Việt Nam. "
        "Phân tích sự kiện và kết quả từ các công cụ được cung cấp. "
        "Trả về một phản hồi JSON với: 'risk_level' (LOW, MEDIUM, HIGH) và 'reasoning' (giải thích ngắn gọn)."
    )

    prompt_parts = [f"Sự kiện cần phân tích: {event_str}"]
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
        return {"risk_level": "UNKNOWN", "reasoning": f"Failed to parse LLM output: {e}. Raw output: {response.text}"}