def search_known_scam_behaviors(query: str) -> list[str]:
    """
    Simulates a search for known scam behaviors based on the query.
    In a real app, this would integrate with a knowledge base or external search API.
    """
    # Simple keyword detection for demonstration
    query_lower = query.lower()
    results = []
    if "miễn phí" in query_lower and ("voucher" in query_lower or "du lịch" in query_lower):
        results.append("Phát hiện từ khóa 'miễn phí' và 'voucher/du lịch' - dấu hiệu phổ biến của các chương trình lừa đảo.")
    if "khách sạn 5 sao" in query_lower and "miễn phí" in query_lower:
        results.append("Gợi ý 'khách sạn 5 sao' và 'miễn phí' thường được dùng trong các chiêu trò dụ dỗ.")
    if "công ty du lịch toàn cầu" in query_lower:
        results.append("Tên 'Công ty du lịch Toàn Cầu' có thể là tên chung được sử dụng bởi các công ty không uy tín. Cần kiểm tra chéo.")
    if "cccd" in query_lower or "ngân hàng" in query_lower:
        results.append("Cảnh báo: Đề cập đến CCCD hoặc tài khoản ngân hàng trong ngữ cảnh không an toàn.")
        
    return results if results else ["Không tìm thấy hành vi lừa đảo cụ thể nào được biết đến."]