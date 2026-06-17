import mysql.connector


class  DB_connection:
    def __init__(self):
        self.create_db()
        self.connect()
        self.create_tables()

    def connect(self):
        self.conn = mysql.connector.connect(
            host = "localhost",
            user = "intelligence-mysql",
            password = "12340",
            database = "Intelligence_db",
            port = 3306
            )

    def get_connection(self):
        if self.conn == None or not self.conn.is_connected():
            self.connect()
        return self.conn

    def create_db(self):
        conn = mysql.connector.connect(
            host = "localhost",
            user = "intelligence-mysql",
            password = "12340",
            port = 3306
            )
        with conn.cursor() as cursor:
            cursor.execute("CREATE DATABASE IF NOT EXISTS Intelligence_db")
        conn.close()

    def create_tables(self):
        query_agents_table = """
            CREATE TABLE IF NOT EXISTS agents (
                id INT PRIMARY KEY AUTO_INCREMENT,
                name VARCHAR(50) NOT NULL,
                specialty VARCHAR(50) NOT NULL,
                is_active BOOLEAN DEFAULT TRUE,
                completed_missions INT DEFAULT 0,
                failed_missions INT DEFAULT 0,
                agent_rank ENUM(Junior / Senior / Commander)
                )
        """
        query_missions_table = """
            CREATE TABLE IF NOT EXISTS missions (
                id INT PRIMARY KEY AUTO_INCREMENT,
                title VARCHAR(100),
                description TEXT,
                location VARCHAR(50),
                difficulty INT CHECK(difficulty BETWEEN 1 AND 10),
                importance CHECK(difficulty BETWEEN 1 AND 10),
                status VARCHAR(30) DEFAULT NEW,
                risk_level VARCHAR(30),
                assigned_agent_id INT DEFAULT NULL
                )
        """
        with self.conn.cursor() as cursor:
            cursor.execute(query_agents_table)
            cursor.execute(query_missions_table)


db = DB_connection()