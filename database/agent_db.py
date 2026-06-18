from .db_connection import db
from .mission_db import missions_manager
from logs.logger_config import logger
    

class AgentDB:

    def create_agent(self, data):
        conn = db.get_connection()
        query = """INSERT INTO agents (name, specialty, agent_rank)
            VALUES (%s, %s, %s)"""
        with conn.cursor() as cursor:
            logger.info("SQL query sent to create a new agent")
            cursor.execute(query, data)
            conn.commit()
            return cursor.rowcount > 0

    def get_all_agents(self):
        conn = db.get_connection()
        with conn.cursor(dictionary=True) as cursor:
            cursor.execute("SELECT * FROM agents")
            all_agents = cursor.fetchall()
        if not all_agents:
            logger.warning("Agents list is empty")
            return []
        return all_agents

    def get_agent_by_id(self, id):
        conn = db.get_connection()
        query = "SELECT * FROM agents WHERE id = %s"
        with conn.cursor(dictionary=True) as cursor:
            cursor.execute(query, [id])
            agent = cursor.fetchone()
            return agent

    def update_agent(self, id, data):
        columns = [f"{column} = %s" for column in list(data.keys())]
        values = list(data.values())+ [id]
        query = f"""UPDATE agents
            SET {", ".join(columns)} WHERE id = %s"""
        conn = db.get_connection()
        with conn.cursor() as cursor:
            logger.info(f"SQL query sent to update agent ID: {id}")
            cursor.execute(query, values)
            conn.commit()
            return cursor.rowcount > 0

    def deactivate_agent(self, id):
        conn=  db.get_connection()
        query = """UPDATE agents
            SET is_active = FALSE WHERE id = %s"""
        with conn.cursor() as cursor:
            logger.info(f"SQL query sent to deactivate agent ID: {id}")
            cursor.execute(query, [id])
            conn.commit()
            return cursor.rowcount > 0

    def increment_completed(self, id):
        conn=  db.get_connection()
        query = """UPDATE agents
            SET completed_missions = completed_missions + 1 WHERE id = %s"""
        with conn.cursor() as cursor:
            cursor.execute(query, [id])
            conn.commit()
            return cursor.rowcount > 0

    def increment_failed(self, id):
        conn=  db.get_connection()
        query = """UPDATE agents
            SET failed_missions = failed_missions + 1 WHERE id = %s"""
        with conn.cursor() as cursor:
            cursor.execute(query, [id])
            conn.commit()
            return cursor.rowcount > 0

    def get_agent_performance(self, id):
        agent = self.get_agent_by_id(id)
        if not agent:
            return None
        open_missions_agent = len(missions_manager.get_open_missions_by_agent(id))
        total_rate = agent["completed_missions"] + agent["failed_missions"] + open_missions_agent
        total_success = 0
        if agent["completed_missions"] + agent["failed_missions"] > 0:
            total_success = (agent["completed_missions"] / total_rate) * 100
        agent_performance = {
            "completed": agent["completed_missions"],
            "failed": agent["failed_missions"],
            "total_success_rate": round(total_success, 3)
            }
        return agent_performance

    def count_active_agents(self):
        conn = db.get_connection()
        query = """SELECT COUNT(*) FROM agents
            WHERE is_active = TRUE"""
        with conn.cursor() as cursor:
            cursor.execute(query)
            all_active_agents = cursor.fetchone()
            return all_active_agents[0] if all_active_agents else 0

agents_manager = AgentDB()