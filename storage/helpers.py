from datetime import datetime
import uuid
import sqlite3


def task_formatter(session_id, task):
    """formats raw task into dict with additional info, id and datetime"""

    assert isinstance(task, str), "task can only be a str"

    task_datetime = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    task_id = str(uuid.uuid4())
    session_id = str(session_id)
    task_text = task
    task_obj = {
        "DATETIME": task_datetime,
        "SESSION_ID": session_id,
        "TASK_ID": task_id,
        "TASK_INPUT": task_text,
    }

    return task_obj


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
