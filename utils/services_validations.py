def validation_rank(data):
    if data["agent_rank"].lower() not in ["junior", "senior", "commander"]:
        return False
    return True


def validation_difficulty_importance(data):
    if (data["difficulty"] < 1 or data["difficulty"] > 10) or (data["importance"] < 1 or data["importance"] > 10):
        return False
    return True


def check_status_rules(status, mission, mission_id):
    errors = {
        1: f"Mission ID: {mission_id} not yet assigned or already in progress",
        2: f"Mission ID: {mission_id} not yet in progress or cancelled",
        3: f"Mission ID: {mission_id} already in progress / completed / failed"
        }
    if status.upper() == "IN_PROGRESS":
        if mission["status"] !="ASSIGNED":
            return errors[1]
    elif status.upper() in ["COMPLETED", "FAILED"]:
        if mission["status"] != "IN_PROGRESS":
            return errors[2]
    elif status.upper() == "CANCELLED":
        if mission["status"] not in ["NEW", "ASSIGNED"]:
            return errors[3]
    else:
        return "OK"


def check_assign_rules(agent, mission, open_missions):
    errors = {
        1: "A critical level mission can only be assigned to a Commander-level agent",
        2: f"Agent ID: {agent["id"]} is not active",
        3: f"Agent ID: {agent["id"]} holds maximum open missions (3)",
        4: f"Mission ID: {mission["id"]} is already assigned to another agent"
        }
    if not  agent["is_active"]:
        return errors[2]
    elif len(open_missions) == 3:
        return errors[3]
    elif mission["risk_level"] == "CRITICAL":
        if agent["agent_rank"] != "commander":
            return errors[1] 
    elif mission["status"] != "NEW":
        return errors[4]
    else:
        return "OK"


def calculate_risk_level(difficulty, importance):
    result = difficulty * 2 + importance
    risk_level = ""
    if 0 <= result < 9: risk_level = "LOW"
    elif 10 <= result < 17: risk_level = "MEDIUM"
    elif 18 <= result < 24: risk_level = "HIGH"
    else: risk_level = "CRITICAL"
    return risk_level