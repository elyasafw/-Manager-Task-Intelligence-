def validation_rank(data):
    if data["agent_rank"].lower() not in ["junior", "senior", "commander"]:
        return False
    return True


def validation_difficulty_importance(data):
    if (data["difficulty"] < 1 or data["difficulty"] > 10) or (data["importance"] < 1 or data["importance"] > 10):
        return False
    return True


def check_status_rules(status, mission, mission_id):
    if status.upper() == "IN_PROGRESS":
        if mission["status"] !="ASSIGNED":
            return f"Mission ID: {mission_id} not yet assigned or already in progress"
    elif status.upper() in ["COMPLETED", "FAILED"]:
        if mission["status"] != "IN_PROGRESS":
            return f"Mission ID: {mission_id} not yet in progress or cancelled"
    elif status.upper() == "CANCELLED":
        if mission["status"] not in ["NEW", "ASSIGNED"]:
            return f"Mission ID: {mission_id} already in progress / completed / failed"
    return "OK"


def check_assign_rules(mission, agent, open_missions):
    if mission["status"] != "NEW":
        return "Mission not available"
    if not agent["is_active"]:
        return f"Agent ID: {agent['id']} is not active"
    if len(open_missions) >= 3:
        return f"Agent ID: {agent['id']} has reached maximum missions"
    if mission["risk_level"] == "CRITICAL":
        if agent["agent_rank"].lower() != "commander":
            return "Only Commander can handle critical missions"
    return "OK"


def calculate_risk_level(difficulty, importance):
    result = difficulty * 2 + importance
    risk_level = ""
    if 0 <= result < 9: risk_level = "LOW"
    elif 10 <= result < 17: risk_level = "MEDIUM"
    elif 18 <= result < 24: risk_level = "HIGH"
    else: risk_level = "CRITICAL"
    return risk_level