from database import SQLstore
from helpers import connection_handler


db=SQLstore()
@connection_handler(db)
def create_test(task):
    print('create_test')
    db.create_table()
    db.create_task(task)

create_test('create a file named test.txt')
db.get_all_tasks()