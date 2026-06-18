def validation_rank(data: dict):
    if data["agent_rank"].lower() not in ["junior", "senior", "commander"]:
        return False
    return True


def validation_difficulty_importance(data: dict):
    if (data["difficulty"] < 1 or data["difficulty"] > 10) or (data["importance"] < 1 or data["importance"] > 10):
        return False
    return True


def calculate_risk_level(difficulty, importance):
    result = difficulty * 2 + importance
    risk_level = ""
    if 0 <= result < 9: risk_level = "LOW"
    elif 10 <= result < 17: risk_level = "MEDIUM"
    elif 18 <= result < 24: risk_level = "HIGH"
    else: risk_level = "CRITICAL"
    return risk_level