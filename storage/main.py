from database import SQLstore
from helpers import connection_handler


db=SQLstore()
@connection_handler(db)
def create_test(task):
    db.create_task(task)

