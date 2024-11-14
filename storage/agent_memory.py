from .database import SQLstore


class AgentMemory(SQLstore):
    def create_agent_memory_table(self):
        """Create a table inside the SQLite DB to store agent memory with the new schema."""
        try:
            if self._sqlconnect is not None:
                # Enable foreign key support
                self._sqlconnect.execute("PRAGMA foreign_keys = ON;")

                # Check if the table already exists
                if self._sqlconnect.execute(
                    "SELECT name FROM sqlite_master WHERE type='table' AND name='agent_memory'"
                ).fetchone():
                    self.logger.info("Table 'agent_memory' already exists")
                    return

                # Create the agent_memory table with the new schema
                self._sqlconnect.execute(
                    """CREATE TABLE agent_memory(
                            ID INTEGER PRIMARY KEY AUTOINCREMENT,
                            SESSION_ID TEXT,
                            TASK_ID TEXT,
                            SUB_TASK_ID TEXT,
                            TIMESTAMP TEXT,
                            SENDER TEXT,
                            MESSAGE_TYPE TEXT,
                            CONTENT TEXT,
                            ARTIFACTS TEXT,
                            AGENT_NAME TEXT,
                            METADATA TEXT,
                            FOREIGN KEY(SESSION_ID) REFERENCES task(SESSION_ID)
                        )"""
                )
                self.logger.info("Table 'agent_memory' created successfully")
            else:
                self.logger.info("Connection to DB not found")
        except sqlite3.Error as e:
            self.logger.error(f"Error occurred in DB: {e}")

    def insert_agent_memory(
        self,
        task_id,
        timestamp,
        sender,
        message_type,
        content=None,
        artifacts=None,
        agent_name=None,
        sub_task_id=None,
        metadata=None,
    ):
        """Insert a new record into the agent_memory table with the new schema."""
        try:
            if self._sqlconnect is not None:
                # Serialize metadata and artifacts to JSON strings if they are dictionaries
                metadata_json = json.dumps(metadata) if metadata else None
                artifacts_json = json.dumps(artifacts) if artifacts else None

                self._sqlconnect.execute(
                    """
                        INSERT INTO agent_memory (
                            SESSION_ID, TASK_ID, SUB_TASK_ID, TIMESTAMP, SENDER,
                            MESSAGE_TYPE, CONTENT, ARTIFACTS, AGENT_NAME, METADATA
                        )
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                    (
                        self._session_id,
                        task_id,
                        sub_task_id,
                        timestamp,
                        sender,
                        message_type,
                        content,
                        artifacts_json,
                        agent_name,
                        metadata_json,
                    ),
                )
                self._sqlconnect.commit()
            else:
                self.logger.info("Connection to DB not found")
        except sqlite3.Error as e:
            self.logger.error(f"Error inserting into agent_memory: {e}")

    def delete_agent_memory(self, task_id=None, session_id=None):
        """Delete entries from agent_memory table based on task_id and/or session_id."""
        try:
            if self._sqlconnect is not None:
                conditions = []
                values = []
                if task_id:
                    conditions.append("TASK_ID = ?")
                    values.append(task_id)
                if session_id:
                    conditions.append("SESSION_ID = ?")
                    values.append(session_id)
                if conditions:
                    where_clause = " WHERE " + " AND ".join(conditions)
                    sql = "DELETE FROM agent_memory" + where_clause
                    self._sqlconnect.execute(sql, values)
                    self._sqlconnect.commit()
                    self.logger.info(
                        "Record(s) deleted successfully from agent_memory."
                    )
                else:
                    self.logger.info("No conditions provided for deletion.")
            else:
                self.logger.info("Connection to DB not found")
        except sqlite3.Error as e:
            self.logger.error(f"Error deleting from agent_memory: {e}")

    def fetch_agent_memory_by_task_id(self, task_id=None, session_id=None):
        """Fetch entries from agent_memory table based on task_id and/or session_id."""
        try:
            if self._sqlconnect is not None:
                conditions = []
                values = []
                if task_id:
                    conditions.append("TASK_ID = ?")
                    values.append(task_id)
                if session_id:
                    conditions.append("SESSION_ID = ?")
                    values.append(session_id)
                if conditions:
                    where_clause = " WHERE " + " AND ".join(conditions)
                else:
                    where_clause = ""
                sql = "SELECT * FROM agent_memory" + where_clause
                cursor = self._sqlconnect.execute(sql, values)
                rows = cursor.fetchall()
                # Process rows to deserialize JSON fields
                result = []
                for row in rows:
                    # Get column names from cursor description
                    column_names = [
                        description[0] for description in cursor.description
                    ]
                    row_dict = dict(zip(column_names, row))
                    # Deserialize METADATA and ARTIFACTS fields
                    if row_dict.get("METADATA"):
                        row_dict["METADATA"] = json.loads(row_dict["METADATA"])
                    if row_dict.get("ARTIFACTS"):
                        row_dict["ARTIFACTS"] = json.loads(row_dict["ARTIFACTS"])
                    result.append(row_dict)
                self.logger.info(f"Fetched {len(result)} record(s) from agent_memory.")
                return result
            else:
                self.logger.info("Connection to DB not found")
                return []
        except sqlite3.Error as e:
            self.logger.error(f"Error fetching from agent_memory: {e}")
            return []

    def fetch_agent_history(self, agent_name, task_id):
        """Fetch and format agent_memory entries into a chat-style format for a given agent_name and task_id."""
        try:
            if self._sqlconnect is not None:
                # Fetch records matching agent_name and task_id, ordered by TIMESTAMP
                cursor = self._sqlconnect.execute(
                    """
                    SELECT SENDER, MESSAGE_TYPE, CONTENT, TIMESTAMP, AGENT_NAME
                    FROM agent_memory
                    WHERE AGENT_NAME = ? AND TASK_ID = ?
                    ORDER BY TIMESTAMP ASC
                    """,
                    (agent_name, task_id),
                )

                rows = cursor.fetchall()

                if not rows:
                    self.logger.info(
                        f"No records found for agent '{agent_name}' with task_id '{task_id}'."
                    )
                    return []
                chat_history = []

                for row in rows:
                    sender, message_type, content, timestamp, agent_name = row
                    # You can customize the format according to your agent's requirements
                    chat_entry = {
                        "sender": sender,
                        "sent_to": agent_name,
                        "message_type": message_type,
                        "content": content,
                        "timestamp": timestamp,
                    }
                    chat_history.append(chat_entry)
                return chat_history
            else:
                self.logger.info("Connection to DB not found")
                return []
        except sqlite3.Error as e:
            self.logger.error(f"Error fetching from agent_memory: {e}")
            return []
