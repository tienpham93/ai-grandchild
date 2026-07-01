import re
import json

def scrub_pii(data: dict) -> dict:
    """
    Anonymizes PII (Personally Identifiable Information) before sending to LLM.
    Scrubs CCCD/CMND (Vietnamese ID cards), bank account numbers, and phone numbers.
    """
    json_str = json.dumps(data, ensure_ascii=False)
    
    # Scrub Phone Numbers (Vietnamese format)
    # Matches formats like 0912345678, 84912345678, +84912345678
    phone_pattern = r'(\+?84|0)(3|5|7|8|9)([0-9]{8})\b'
    json_str = re.sub(phone_pattern, '[REDACTED_PHONE]', json_str)
    
    # Scrub CCCD (12 digits) / CMND (9 digits)
    cccd_pattern = r'\b([0-9]{9}|[0-9]{12})\b'
    json_str = re.sub(cccd_pattern, '[REDACTED_ID]', json_str)
    
    # Scrub Bank Account/Card numbers in text (e.g. "TK 10293")
    # Matches patterns like TK followed by digits, or 16 digit card numbers
    bank_pattern = r'\b(?:TK|STK)\s*[:\-]?\s*([0-9\s]{5,16})\b'
    json_str = re.sub(bank_pattern, 'TK [REDACTED_BANK]', json_str, flags=re.IGNORECASE)

    # Note: 16-digit card numbers could also be matched if needed
    card_pattern = r'\b([0-9]{4}[\s\-]*){3}[0-9]{4}\b'
    json_str = re.sub(card_pattern, '[REDACTED_CARD]', json_str)
    
    return json.loads(json_str)

if __name__ == "__main__":
    test_data = {
        "text": "Senior number: 0912345678, Idenity card: 079012345678. Bank Account 123456789 NAB"
    }
    print(scrub_pii(test_data))
