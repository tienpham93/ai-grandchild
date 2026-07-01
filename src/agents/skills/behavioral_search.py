SCAM_RULES = [
    {
        "must_have": ["free"],
        "any_of": ["voucher", "vacation", "lunch"],
        "signal": "Signal: Approach via 'free' vacation/lunch vouchers to lure elderly targets."
    },
    {
        "must_have": ["grand hotel", "ballroom"],
        "any_of": [],
        "signal": "Signal: Hosting high-pressure sales presentations in rented high-end ballrooms."
    },
    {
        "must_have": [],
        "any_of": ["charge", "withdrawn", "transaction"],
        "signal": "Signal: Large, sudden financial transaction occurs with no clear contract details."
    }
]

def search_known_scam_behaviors(query: str) -> list[str]:
    """
    Evaluates typical behavioral triggers linked to timeshare rings and high-pressure sales
    using a declarative, data-driven rules engine.
    """
    query_lower = query.lower()
    signals = []
    
    for rule in SCAM_RULES:
        # Check if ALL keywords in "must_have" are present
        must_match = all(kw in query_lower for kw in rule["must_have"]) if rule["must_have"] else True
        
        # Check if AT LEAST ONE keyword in "any_of" is present
        any_match = any(kw in query_lower for kw in rule["any_of"]) if rule["any_of"] else True
        
        if must_match and any_match:
            signals.append(rule["signal"])
            
    return signals if signals else ["No explicit scam signatures detected."]