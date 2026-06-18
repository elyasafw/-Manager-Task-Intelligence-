import mysql.connector
from logs.logger_config import logger


class  DB_connection:
    def __init__(self):
        self.conn = None

    def connect(self):
        self.conn = mysql.connector.connect(
            host = "localhost",
            user = "root",
            password = "1234",
            database = "Intelligence_db",
            port = 3306
            )
        logger.info("Connection to the database was successful")

    def get_connection(self):
        if self.conn == None or not self.conn.is_connected():
            self.connect()
        return self.conn

    def create_db(self):
        conn = mysql.connector.connect(
            host = "localhost",
            user = "root",
            password = "1234",
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
                agent_rank ENUM('junior', 'senior', 'commander')
                )
        """
        query_missions_table = """
            CREATE TABLE IF NOT EXISTS missions (
                id INT PRIMARY KEY AUTO_INCREMENT,
                title VARCHAR(100),
                description TEXT,
                location VARCHAR(50),
                difficulty INT CHECK(difficulty BETWEEN 1 AND 10),
                importance INT CHECK(importance BETWEEN 1 AND 10),
                status VARCHAR(30) DEFAULT 'NEW',
                risk_level VARCHAR(30),
                assigned_agent_id INT DEFAULT NULL
                )
        """
        with self.conn.cursor() as cursor:
            cursor.execute(query_agents_table)
            logger.info("Agents table ready")
            cursor.execute(query_missions_table)
            logger.info("Missions table ready")

    def close_connection(self):
        self.conn.close()
        logger.info("The database was closed successfully")


db = DB_connection()