from .db_connection import db
from pydantic import BaseModel


class NewAgent(BaseModel):
    name : str
    specialty : str
    agent_rank : str

class UpdateAgent(BaseModel):
    name : str | None = None
    specialty : str | None = None
    agent_rank : str | None = None


# Temporary utility functions
def validation_rank(data: dict):
    if data["agent_rank"].lower() not in ["junior, senior, commander"]:
        print("The 'agent_rank' field must only be: Junior / Senior / Commander")
        return False
    return True
    

class AgentDB:

    def create_agent(self, data: NewAgent):
        new_agent = data.model_dump()
        if not validation_rank(new_agent):
            return
        values = [new_agent["name"], new_agent["specialty"], new_agent["agent_rank"]]
        conn = db.get_connection()
        query = """INSERT INTO agents (name, specialty, agent_rank)
            VALUES (%s, %s, %s)"""
        with conn.cursor() as cursor:
            cursor.execute(query, values)
            conn.commit()
            if not cursor.rowcount > 0:
                return "Creating a new agent failed..."
            return {"name": data[0], "specialty": data[1], "agent_rank": data[2]}

    def get_all_agents(self):
        conn = db.get_connection()
        with conn.cursor(dictionary=True) as cursor:
            cursor.execute("SELECT * FROM agents")
            all_agents = cursor.fetchall()
        if not all_agents:
            return []
        return all_agents

    def get_agent_by_id(self, id):
        conn = db.get_connection()
        query = "ELECT * FROM agents WHERE id = %s"
        with conn.cursor(dictionary=True) as cursor:
            cursor.execute(query, [id])
            agent = cursor.fetchone()
        if not agent:
            return None
        return agent

    def update_agent(self, id, data: UpdateAgent):
        update_agent = data.model_dump(exclude_none=True)
        if "agent_rank" in update_agent:
            if not validation_rank(update_agent):
                return
        columns = [f"{column} = %s" for column in list(update_agent.keys())]
        values = list(update_agent.values())+ [id]
        query = f"""UPDATE agents
            SET ({", ".join(columns)}) WHERE id = %s"""
        conn = db.get_connection()
        with conn.cursor() as cursor:
            cursor.execute(query, values)
            conn.commit()
            if not cursor.rowcount > 0:
                return f"Agent ID: {id} update failed..."
            return f"Agent ID: {id} successfully updated"

    def deactivate_agent(self, id):
        conn=  db.get_connection()
        query = """UPDATE agents
            SET is_active = FALSE WHERE id = %s"""
        with conn.cursor() as cursor:
            cursor.execute(query, [id])
            conn.commit()
            if not cursor.rowcount > 0:
                return f"Agent ID: {id} deactivate failed..."
            return f"Agent ID: {id} successfully deactivated"

    def increment_completed(self, id):
        conn=  db.get_connection()
        query = """UPDATE agents
            SET completed_missions += 1 WHERE id = %s"""
        with conn.cursor() as cursor:
            cursor.execute(query, [id])
            conn.commit()
            if not cursor.rowcount > 0:
                return f"Updating completed missions of Agent ID: {id} failed..."
            return f"Agent ID: {id} Added 1 mission successfully completed"

    def increment_failed(self, id):
        conn=  db.get_connection()
        query = """UPDATE agents
            SET failed_missions += 1 WHERE id = %s"""
        with conn.cursor() as cursor:
            cursor.execute(query, [id])
            conn.commit()
            if not cursor.rowcount > 0:
                return f"Updating failed missions of Agent ID: {id} failed..."
            return f"Agent ID: {id} Added 1 failed mission successfully"

    def get_agent_performance(self, id):
        agent = self.get_agent_by_id(id)
        if not agent:
            return f"Agent ID: {id} not found"
        total_rate = agent["completed_missions"] + agent["failed_missions"]
        total_success = 0
        if agent["completed_missions"] + agent["failed_missions"] > 0:
            total_success = (agent["completed_missions"] / total_rate) * 100
        agent_performance = {
            "completed": agent["completed_missions"],
            "failed": agent["failed_missions"],
            "total, success_rate": total_success
            }
        return agent_performance()