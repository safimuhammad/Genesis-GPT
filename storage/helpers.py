from datetime import datetime
import uuid
import sqlite3
import json
from typing import Union, Dict, Any


def task_formatter(session_id: str, task: Union[str, Dict[str, Any]], custom_id: str = None) -> Dict[str, str]:
    """
    Formats raw task into dict with additional info, id and datetime.
    
    Args:
        session_id: The session identifier
        task: Either a string message or a dictionary containing task data
        custom_id: Optional custom identifier for the task
        
    Returns:
        Dictionary containing formatted task data
    """
    task_datetime = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    task_id = custom_id if custom_id is not None else str(uuid.uuid4())
    session_id = str(session_id)

    if isinstance(task, dict):
        task_type = task.get('type', 'INPUT')
        task_payload = task.get('payload', '')
        if isinstance(task_payload, (dict, list)):
            task_payload = json.dumps(task_payload)
        elif not isinstance(task_payload, str):
            task_payload = str(task_payload)
    else:
        task_type = "OUTPUT" if custom_id else "INPUT"
        task_payload = str(task)

    return {
        "DATETIME": task_datetime,
        "SESSION_ID": session_id,
        "TASK_ID": task_id,
        "TASK_PAYLOAD": task_payload,
        "TYPE": task_type
    }


def connection_handler(db):

    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                if db.get_connection == None:
                    db.create_connection()
                    return func(*args, **kwargs)
            except Exception as e:
                db.logger.error(f"Error occurred: {e}")

        return wrapper

    return decorator
