from .interface import IDatabase
import sqlite3
import logging
import json
import uuid
from .helpers import task_formatter, connection_handler


class SQLstore(IDatabase):
    def __init__(self):
        """Initializing logging and connections"""

        logging.basicConfig(level=logging.DEBUG)
        self.logger = logging.getLogger("SQLstore")
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        # Unique session ID
        self._session_id = str(uuid.uuid4())

        self._sqlconnect = self.create_connection

        for handler_type in [logging.FileHandler, logging.StreamHandler]:
            handler = (
                handler_type("db.log")
                if handler_type == logging.FileHandler
                else handler_type()
            )
            handler.setLevel(
                logging.INFO if handler_type == logging.FileHandler else logging.DEBUG
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

    @property
    def get_connection(self):
        """function to check the connection"""
        return self._sqlconnect

    @property
    def get_session_id(self):
        """function to get the current session ID"""
        return self._session_id

    @property
    def create_connection(self):
        """function to create connection"""
        try:
            connection = sqlite3.connect("sql.db")
            # self.logger.info(f"Connection created successfully")
            return connection
        except sqlite3.Error as e:
            self.logger.error(f"Error occured while creating connection: {e}")

    def create_table(self):
        """create a table inside the SQLite DB"""
        try:
            if self._sqlconnect is not None:
                # base case
                if table_or_not := self._sqlconnect.execute(
                    f"SELECT name FROM sqlite_master WHERE type='table' AND name='task'"
                ).fetchone():
                    return self.logger.info(f"Table already exists")

                self._sqlconnect.execute(
                    f"""CREATE TABLE task(
                    DATETIME TEXT, SESSION_ID TEXT PRIMARY KEY,TASK_ID TEXT , TASK_INPUT TEXT
                )"""
                )
                self.logger.info(f"Table created successfully")

            else:
                self.logger.info(f"Connection to DB not found")

        except sqlite3.Error as e:
            self.logger.error(f"Error occured in DB: {e}")

    def add_task(self, task):
        """creates a task by assigning it unique id and datetime"""
        try:
            meta_data = task_formatter(self._session_id, task)
            assert isinstance(
                meta_data, dict
            ), f"data should be in dict not {type(meta_data)} "
            assert all(
                key in meta_data
                for key in ["DATETIME", "TASK_ID", "TASK_INPUT", "SESSION_ID"]
            ), "data should have DATETIME, TASK_ID, and TASK_INPUT keys"  # verifying keys

            if self._sqlconnect != None:
                self._sqlconnect.execute(
                    """INSERT INTO task (DATETIME,SESSION_ID, TASK_ID, TASK_INPUT)
                VALUES(?,?,?,?)

                """,
                    (
                        meta_data["DATETIME"],
                        meta_data["SESSION_ID"],
                        meta_data["TASK_ID"],
                        meta_data["TASK_INPUT"],
                    ),
                )

                self._sqlconnect.commit()
                self.logger.info(
                    f"Task_id:{meta_data['TASK_ID']} Task_input:{meta_data['TASK_INPUT']} created at:{meta_data['DATETIME']}"
                )
                return meta_data["TASK_ID"]
            else:
                self.logger.info(f"Connection to DB not found")

        except sqlite3.Error as e:
            self.logger.error(f"Error occurred in DB while inserting: {e}")

    def create_task_plan_table(self):
        """Create a table inside the SQLite DB to store task plans"""
        try:
            if self._sqlconnect is not None:
                # Check if the table already exists
                if self._sqlconnect.execute(
                    "SELECT name FROM sqlite_master WHERE type='table' AND name='task_plan'"
                ).fetchone():
                    return self.logger.info("Table 'task_plan' already exists")

                # Create the task_plan table
                self._sqlconnect.execute(
                    """CREATE TABLE task_plan(
                        ID INTEGER PRIMARY KEY AUTOINCREMENT,
                        SESSION_ID TEXT,
                        TASK_ID TEXT,
                        THOUGHTS TEXT,
                        GRAPH TEXT,
                        ABILITY TEXT,
                        FOREIGN KEY(SESSION_ID) REFERENCES task(SESSION_ID)
                    )"""
                )
                self.logger.info("Table 'task_plan' created successfully")
            else:
                self.logger.info("Connection to DB not found")
        except sqlite3.Error as e:
            self.logger.error(f"Error occurred in DB: {e}")

    def add_task_plan(self, task_id, plan_data):
        """Insert a new task plan into the task_plan table"""
        try:
            # Ensure plan_data is a dictionary
            assert isinstance(
                plan_data, dict
            ), f"data should be in dict, not {type(plan_data)}"

            # Extract the required parts from the JSON
            thoughts = json.dumps(
                plan_data.get("thoughts", [])
            )  # Convert list to JSON string
            graph = json.dumps(
                plan_data.get("graph", [])
            )  # Convert list to JSON string
            ability = json.dumps(
                plan_data.get("ability", [])
            )  # Convert list to JSON string

            if self._sqlconnect is not None:
                self._sqlconnect.execute(
                    """INSERT INTO task_plan (SESSION_ID, TASK_ID, THOUGHTS, GRAPH, ABILITY)
                    VALUES (?, ?, ?, ?, ?)""",
                    (
                        self._session_id,  # Use the session ID generated in the __init__
                        task_id,  # Task ID from the original task
                        thoughts,
                        graph,
                        ability,
                    ),
                )

                self._sqlconnect.commit()
                self.logger.info(
                    f"Task Plan for Task ID {task_id} created successfully."
                )
            else:
                self.logger.info("Connection to DB not found")

        except sqlite3.Error as e:
            self.logger.error(f"Error occurred in DB: {e}")

    def delete_task(self, task_id):
        """Delete a single task based on task_id"""
        try:
            if self._sqlconnect != None:
                # base case
                if self._sqlconnect.execute(
                    "SELECT * FROM task WHERE TASK_ID=?", (task_id,)
                ).fetchone():
                    self._sqlconnect.execute(
                        "DELETE FROM task WHERE TASK_ID=?", (task_id,)
                    )
                    self._sqlconnect.commit()
                    self.logger.info(f"task_id: {task_id} deleted successfully")
                else:
                    self.logger.error(f"task: {task_id} does not exist.")
            else:
                self.logger.info(f"Connection to DB not found")

        except sqlite3.Error as e:
            self.logger.error(f"Failed to delete task_id {task_id}: {e}")

    def get_all_tasks(self):
        """Fetches all tasks from the db"""
        return self._sqlconnect.execute("""SELECT * FROM task""").fetchall()

    def update_task(self, task_id, task_input):
        """Updates task based on task_id"""
        try:
            if self._sqlconnect != None:
                self._sqlconnect.execute(
                    "UPDATE task SET TASK_INPUT=? WHERE TASK_ID=?",
                    (task_input, task_id),
                )
                self._sqlconnect.commit()
                self.logger.info(f"task_id:{task_id} updated successfully")
            else:
                self.logger.error("Connection to DB not found")
        except sqlite3.Error as e:
            self.logger.error(f"Error updating task_id: {task_id} caused by {e}")

    def get_task(self, task_id):
        """Gets the specific task based on task_id"""
        try:
            if self._sqlconnect != None:
                task = self._sqlconnect.execute(
                    "SELECT * FROM task WHERE TASK_ID=?", (task_id,)
                ).fetchone()

                return (
                    task
                    if task
                    else self.logger.error(f"task: {task_id} does not exist")
                )
        except sqlite3.Error as e:
            self.logger.error(
                f"Error occurred while fetching task_id {task_id} due to: {e}"
            )
