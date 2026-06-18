from db_connection import db
    

class AgentDB:

    def create_agent(self, data):
        conn = db.get_connection()
        query = """INSERT INTO agents (name, specialty, agent_rank)
            VALUES (%s, %s, %s)"""
        with conn.cursor() as cursor:
            cursor.execute(query, data)
            conn.commit()
            return cursor.rowcount > 0

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
        query = "SELECT * FROM agents WHERE id = %s"
        with conn.cursor(dictionary=True) as cursor:
            cursor.execute(query, [id])
            agent = cursor.fetchone()
        if not agent:
            return None
        return agent

    def update_agent(self, id, data):
        columns = [f"{column} = %s" for column in list(data.keys())]
        values = list(data.values())+ [id]
        query = f"""UPDATE agents
            SET {", ".join(columns)} WHERE id = %s"""
        conn = db.get_connection()
        with conn.cursor() as cursor:
            cursor.execute(query, values)
            conn.commit()
            return cursor.rowcount > 0

    def deactivate_agent(self, id):
        conn=  db.get_connection()
        query = """UPDATE agents
            SET is_active = FALSE WHERE id = %s"""
        with conn.cursor() as cursor:
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
            if not cursor.rowcount > 0:
                return f"Updating completed missions of Agent ID: {id} failed..."
            return f"Agent ID: {id} Added 1 mission successfully completed"

    def increment_failed(self, id):
        conn=  db.get_connection()
        query = """UPDATE agents
            SET failed_missions = failed_missions + 1 WHERE id = %s"""
        with conn.cursor() as cursor:
            cursor.execute(query, [id])
            conn.commit()
            if not cursor.rowcount > 0:
                return f"Updating failed missions of Agent ID: {id} failed..."
            return f"Agent ID: {id} Added 1 failed mission successfully"

    def get_agent_performance(self, id):
        agent = self.get_agent_by_id(id)
        if not agent:
            return None
        total_rate = agent["completed_missions"] + agent["failed_missions"]
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
        with conn.cursor(dictionary=True) as cursor:
            cursor.execute("SELECT * FROM agents WHERE is_active = TRUE")
            all_active_agents = cursor.fetchall()
            return all_active_agents

agents_manager = AgentDB()