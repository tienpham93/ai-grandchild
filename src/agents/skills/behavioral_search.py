def search_known_scam_behaviors(query: str) -> list[str]:
    """
    Simulates a search for known scam behaviors based on the query.
    In a real app, this would integrate with a knowledge base or external search API.
    """
    
    query_lower = query.lower()
    signals = []
    
    if "free" in query_lower and ("voucher" in query_lower or "vacation" in query_lower or "lunch" in query_lower):
        signals.append("Signal: Approach via 'free' vacation/lunch vouchers to lure elderly targets.")
    if "grand hotel" in query_lower and "ballroom" in query_lower:
        signals.append("Signal: Hosting high-pressure sales presentations in rented high-end ballrooms.")
    if "charge" in query_lower or "withdrawn" in query_lower or "transaction" in query_lower:
        signals.append("Signal: Large, sudden financial transaction occurs with no clear contract details.")
        
    return signals if signals else ["No explicit scam signatures detected."]