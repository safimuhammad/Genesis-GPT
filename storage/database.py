from .interface import IDatabase
import sqlite3
import logging
import json
import uuid
from .helpers import task_formatter, connection_handler
from contextlib import contextmanager
from queue import Queue
from typing import Optional, List, Dict, Any
import threading

class ConnectionPool:
    def __init__(self, max_connections=5):
        self.max_connections = max_connections
        self.connections: Queue = Queue(maxsize=max_connections)
        self.active_connections = 0
        self.lock = threading.Lock()

    def get_connection(self) -> Optional[sqlite3.Connection]:
        with self.lock:
            if self.connections.empty() and self.active_connections < self.max_connections:
                conn = sqlite3.connect("sql.db", check_same_thread=False)
                conn.row_factory = sqlite3.Row
                self.active_connections += 1
                return conn
        connection = self.connections.get()
        return connection

    def return_connection(self, connection: sqlite3.Connection):
        self.connections.put(connection)

class SQLstore(IDatabase):
    def __init__(self):
        logging.basicConfig(level=logging.DEBUG)
        self.logger = logging.getLogger("SQLstore")
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        self._session_id = str(uuid.uuid4())
        self.connection_pool = ConnectionPool()
        for handler_type in [logging.FileHandler, logging.StreamHandler]:
            handler = handler_type("db.log") if handler_type == logging.FileHandler else handler_type()
            handler.setLevel(logging.INFO if handler_type == logging.FileHandler else logging.DEBUG)
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
        self._initialize_database()

    @contextmanager
    def get_db_connection(self):
        connection = self.connection_pool.get_connection()
        try:
            yield connection
        finally:
            if connection:
                self.connection_pool.return_connection(connection)

    def _initialize_database(self):
        with self.get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS task (
                    DATETIME TEXT,
                    SESSION_ID TEXT,
                    TASK_ID TEXT PRIMARY KEY,
                    TASK_PAYLOAD TEXT,
                    TYPE TEXT
                )
            """)
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_task_id ON task(TASK_ID)")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS task_plan (
                    ID INTEGER PRIMARY KEY AUTOINCREMENT,
                    SESSION_ID TEXT,
                    TASK_ID TEXT,
                    THOUGHTS TEXT,
                    GRAPH TEXT,
                    ABILITY TEXT,
                    FOREIGN KEY(SESSION_ID) REFERENCES task(SESSION_ID)
                )
            """)
            conn.commit()

    def create_table(self):
        pass  # Already handled in _initialize_database

    def add_task(self, task: Dict[str, Any], custom_id: str = None) -> Optional[str]:
        try:
            meta_data = task_formatter(self._session_id, task, custom_id)
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """INSERT INTO task (DATETIME, SESSION_ID, TASK_ID, TASK_PAYLOAD, TYPE)
                    VALUES (?, ?, ?, ?, ?)""",
                    (
                        meta_data["DATETIME"],
                        meta_data["SESSION_ID"],
                        meta_data["TASK_ID"],
                        meta_data["TASK_PAYLOAD"],
                        meta_data["TYPE"]
                    )
                )
                conn.commit()
                self.logger.info(f"Task {meta_data['TASK_ID']} added successfully")
                return meta_data["TASK_ID"]
        except Exception as e:
            self.logger.error(f"Error adding task: {e}")
            return None

    def add_task_plan(self, task_id: str, plan_data: Dict[str, Any]) -> bool:
        try:
            thoughts = json.dumps(plan_data.get("thoughts", []))
            graph = json.dumps(plan_data.get("graph", []))
            ability = json.dumps(plan_data.get("ability", []))
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """INSERT INTO task_plan (SESSION_ID, TASK_ID, THOUGHTS, GRAPH, ABILITY)
                    VALUES (?, ?, ?, ?, ?)""",
                    (self._session_id, task_id, thoughts, graph, ability)
                )
                conn.commit()
                self.logger.info(f"Task Plan for Task ID {task_id} created successfully")
                return True
        except Exception as e:
            self.logger.error(f"Error adding task plan: {e}")
            return False

    def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM task WHERE TASK_ID = ?", (task_id,))
                result = cursor.fetchone()
                return dict(result) if result else None
        except Exception as e:
            self.logger.error(f"Error retrieving task {task_id}: {e}")
            return None

    def get_all_tasks(self) -> List[Dict[str, Any]]:
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM task")
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            self.logger.error(f"Error retrieving all tasks: {e}")
            return []

    def update_task(self, task_id: str, task_input: Dict[str, Any]) -> bool:
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """UPDATE task 
                    SET TASK_PAYLOAD = ?
                    WHERE TASK_ID = ?""",
                    (json.dumps(task_input), task_id)
                )
                conn.commit()
                if cursor.rowcount > 0:
                    self.logger.info(f"Task {task_id} updated successfully")
                    return True
                self.logger.warning(f"No task found with ID {task_id}")
                return False
        except Exception as e:
            self.logger.error(f"Error updating task {task_id}: {e}")
            return False

    def delete_task(self, task_id: str) -> bool:
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM task WHERE TASK_ID = ?", (task_id,))
                conn.commit()
                if cursor.rowcount > 0:
                    self.logger.info(f"Task {task_id} deleted successfully")
                    return True
                self.logger.warning(f"No task found with ID {task_id}")
                return False
        except Exception as e:
            self.logger.error(f"Error deleting task {task_id}: {e}")
            return False