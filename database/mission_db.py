from db_connection import db
from agent_db import agents_manager
from pydantic import BaseModel


class NewMission(BaseModel):
    title : str
    description : str
    location : str
    difficulty : int
    importance : int


# Temporary utility functions
def validation_difficulty_importance(data: dict):
    if (data["difficulty"] < 1 or data["difficulty"] > 10) or (data["importance"] < 1 or data["importance"] > 10):
        print("The 'difficulty' and 'importance' fields must be in the range of 1-10")
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


class MissionDB:

    def create_mission(self, data: NewMission):
        new_mission = data.model_dump()
        if not validation_difficulty_importance(new_mission):
            return
        risk_level = calculate_risk_level(new_mission["difficulty"], new_mission["importance"])
        values = [
            new_mission["title"],
            new_mission["description"],
            new_mission["location"],
            new_mission["difficulty"],
            new_mission["importance"],
            risk_level
            ]
        conn = db.get_connection()
        query = """INSERT INTO missions (title, description, location, difficulty, importance, risk_level)
            VALUES (%s, %s, %s , %s, %s, %s)"""
        with conn.cursor() as cursor:
            cursor.execute(query, values)
            conn.commit()
            if not cursor.rowcount > 0:
                return "Creating a new mission failed..."
            return new_mission

    def get_all_missions(self):
        conn = db.get_connection()
        with conn.cursor(dictionary=True) as cursor:
            cursor.execute("SELECT * FROM missions")
            all_missions = cursor.fetchall()
        if not all_missions:
            return []
        return all_missions

    def get_mission_by_id(self, id):
        conn = db.get_connection()
        query = "SELECT * FROM missions WHERE id = %s"
        with conn.cursor(dictionary=True) as cursor:
            cursor.execute(query, [id])
            mission = cursor.fetchone()
        if not mission:
            return None
        return mission

    def assign_mission(self, m_id, a_id):
        mission = self.get_mission_by_id(m_id)
        if not mission:
            return f"Mission ID: {m_id} not found"
        elif mission["status"] != "NEW":
            return f"Mission ID: {m_id} is already assigned to another agent"
        elif mission["risk_level"] == "CRITICAL":
            agent = agents_manager.get_agent_by_id(a_id)
            if not agent:
                return f"Agent ID: {a_id} not found"
            elif agent["agent_rank"] != "commander":
                return "A critical level mission can only be assigned to a Commander-level agent"
            elif not  agent["is_active"]:
                return f"Agent ID: {a_id} is deactivated"
        query = """UPDATE missions
            SET status = 'ASSIGNED', assigned_agent_id = %s
            WHERE id = %s"""
        conn = db.get_connection()
        with conn.cursor() as cursor:
            cursor.execute(query, [a_id, m_id])
            conn.commit()
            if not cursor.rowcount > 0:
                return f"Assignment of mission ID: {m_id} to agent ID: {a_id} failed"
            return f"Mission ID: {m_id} was successfully assigned to Agent ID: {a_id}"

    def update_mission_status(self, id, status):
        mission = self.get_mission_by_id(id)
        if not mission:
            return f"Mission ID: {id} not found"
        if status.upper() == "IN_PROGRESS":
            if mission["status"] !="ASSIGNED":
                return f"Mission ID: {id} not yet assigned or already in progress"
        elif status.upper() in ["COMPLETED", "FAILED"]:
            if mission["status"] != "IN_PROGRESS":
                return f"Mission ID: {id} not yet in progress or cancelled"
        elif status.upper() == "CANCELLED":
            if mission["status"] not in ["NEW", "ASSIGNED"]:
                return f"Mission ID: {id} already in progress / completed / failed"
        elif status.upper() == "ASSIGNED":
            if mission["status"] == "NEW":
                return "Cannot assign a mission without an agent ID."
        query = """UPDATE missions
            SET status = %s WHERE id = %s"""
        conn = db.get_connection()
        with conn.cursor() as cursor:
            cursor.execute(query, [status, id])
            conn.commit()
            if not cursor.rowcount > 0:
                return f"Change mission Status ID: {id} failed"
            return f"Change mission Status ID: {id} Updated Successfully"

    def get_open_missions_by_agent(self, id):
        conn = db.get_connection()
        query = """SELECT * FROM missions
            WHERE assigned_agent_id = %s AND (status = 'ASSIGNED' OR status = 'IN_PROGRESS')"""
        conn = db.get_connection()
        with conn.cursor(dictionary=True) as cursor:
            cursor.execute(query, [id])
            all_open_missions = cursor.fetchall()
            if not all_open_missions:
                return f"Agent ID: {id} No open missions"
            return all_open_missions

    def count_all_missions(self):
        conn = db.get_connection()
        query = """SELECT COUNT(*) FROM missions"""
        with conn.cursor() as cursor:
            cursor.execute(query)
            count_missions = cursor.fetchone()
            return count_missions[0] if count_missions else 0

    def count_by_status(self, status):
        conn = db.get_connection()
        query = """SELECT COUNT(*) FROM missions
            WHERE status = %s"""
        with conn.cursor() as cursor:
            cursor.execute(query, [status])
            count_status = cursor.fetchone()
            return count_status[0] if count_status else 0

    def count_open_missions(self):
        conn = db.get_connection()
        query = """SELECT COUNT(*) FROM missions
            WHERE status = 'ASSIGNED' OR status = 'IN_PROGRESS'"""
        with conn.cursor() as cursor:
            cursor.execute(query)
            open_missions = cursor.fetchone()
            return open_missions[0] if open_missions else 0

    def count_critical_missions(self):
        conn = db.get_connection()
        query = """SELECT COUNT(*) FROM missions
            WHERE risk_level = 'CRITICAL'"""
        with conn.cursor() as cursor:
            cursor.execute(query)
            critical_missions = cursor.fetchone()
            return critical_missions[0] if critical_missions else 0

    def get_top_agent(self):
        conn = db.get_connection()
        query = """SELECT * FROM agents 
            ORDER BY completed_missions DESC
            LIMIT 1"""
        with conn.cursor(dictionary=True) as cursor:
            cursor.execute(query)
            top_agent= cursor.fetchone()
        return top_agent