from dataclasses import dataclass, field
from typing import Optional, List
import sqlite3

from student_assistant.core.config import settings
from student_assistant.project import Project



@dataclass
class ProjectDB:
    db_path: str = field(default=settings.DB_PATH)

    def __post_init__(self):
        self._init_db()

    def create_project(self, name: str) -> int:
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO projects (name) VALUES (?)", (name,))
            conn.commit()
            return cursor.lastrowid
    
    def get_project_by_name(self, name: str) -> Optional[dict]:
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, name FROM projects WHERE name = ?", (name,))
            row = cursor.fetchone()
            if row:
                return Project(id=row[0], name=row[1])
            return None

    def get_project_id(self, name: str) -> Optional[int]:
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM projects WHERE name = ?", (name,))
            row = cursor.fetchone()
            return row[0] if row else None

    def list_projects(self) -> List[str]:
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM projects")
            return [row[0] for row in cursor.fetchall()]

    def add_document(self, project_id: int, filename: str):
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO documents (name, project_id) VALUES (?, ?)",
                (filename, project_id)
            )
            conn.commit()

    def list_documents(self, project_id: int) -> List[str]:
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM documents WHERE project_id = ?", (project_id,))
            return [row[0] for row in cursor.fetchall()]
    
    def delete_project(self, project_id: int):
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM projects WHERE id = ?", (project_id,))
            cursor.execute("DELETE FROM documents WHERE project_id = ?", (project_id,))
            conn.commit()

    def _connect(self):
        return sqlite3.connect(self.db_path)

    def _init_db(self):
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS projects (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS documents (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    project_id INTEGER NOT NULL,
                    FOREIGN KEY (project_id) REFERENCES projects(id)
                )
            """)
            conn.commit()