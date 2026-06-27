def verify_high_risk_location(address: str, latitude: str, longitude: str) -> bool:
    """
    Mock geofencing tool. 
    Verifies if a location matches known high-risk venues for timeshare scams.
    These are often luxury hotels (e.g., 5-star hotels in district centers)
    used for "customer appreciation" seminars.
    """
    # In a real app, this would check against a geospatial database of known scam venues.
    # We mock it here based on common keywords.
    high_risk_keywords = ["hotel", "resort", "ballroom", "5 sao", "5-star"]
    
    address_lower = address.lower()
    for keyword in high_risk_keywords:
        if keyword in address_lower:
            return True
            
    return False
