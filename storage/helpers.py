from datetime import datetime
import uuid

def task_formatter(task):
    """formats raw task into dict with additional info, id and datetime"""

    assert isinstance(task,str), "task can only be a str"

    task_datetime= datetime.now().strftime('%d/%m/%Y %H:%M:%S')
    task_id= str(uuid.uuid4())
    task_text= task
    task_obj={'DATETIME':task_datetime,'TASK_ID':task_id,'TASK_INPUT':task_text}

    return task_obj







