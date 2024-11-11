from components.models import Project, ProjectTask
import mysql.connector
from config import DB_HOST, DB_USER, DB_PASSWORD, DB_NAME

class DatabaseConnector:
    def __init__(self):
        self.host = DB_HOST
        self.user = DB_USER
        self.password = DB_PASSWORD
        self.database = DB_NAME

    def connect(self):
        return mysql.connector.connect(
            host=self.host,
            user=self.user,
            password=self.password,
            database=self.database
        )

    def fetch_projects(self):
        conn = self.connect()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, nombre, estado, fecha_inicio, fecha_fin FROM projects")
        projects = [Project(**row) for row in cursor.fetchall()]
        cursor.close()
        conn.close()
        return projects

    def fetch_project_tasks(self, query):
        conn = self.connect()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query)
        tasks = [ProjectTask(**row) for row in cursor.fetchall()]
        cursor.close()
        conn.close()
        return tasks


