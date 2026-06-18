from db_connection import db
from agent_db import agents_manager


class MissionDB:

    def create_mission(self, data):
        conn = db.get_connection()
        query = """INSERT INTO missions (title, description, location, difficulty, importance, risk_level)
            VALUES (%s, %s, %s , %s, %s, %s)"""
        with conn.cursor() as cursor:
            cursor.execute(query, data)
            conn.commit()
            return cursor.rowcount > 0

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
        query = """UPDATE missions
            SET status = 'ASSIGNED', assigned_agent_id = %s
            WHERE id = %s"""
        conn = db.get_connection()
        with conn.cursor() as cursor:
            cursor.execute(query, [a_id, m_id])
            conn.commit()
            return cursor.rowcount > 0

    def update_mission_status(self, id, status):
        query = """UPDATE missions
            SET status = %s WHERE id = %s"""
        conn = db.get_connection()
        with conn.cursor() as cursor:
            cursor.execute(query, [status, id])
            conn.commit()
            return cursor.rowcount > 0

    def get_open_missions_by_agent(self, id):
        conn = db.get_connection()
        query = """SELECT * FROM missions
            WHERE assigned_agent_id = %s AND (status = 'ASSIGNED' OR status = 'IN_PROGRESS')"""
        conn = db.get_connection()
        with conn.cursor(dictionary=True) as cursor:
            cursor.execute(query, [id])
            all_open_missions = cursor.fetchall()
            if not all_open_missions:
                return []
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


missions_manager=  MissionDB()