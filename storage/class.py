from database import IDatabase
import sqlite3
import logging
import uuid
from helpers import task_formatter


class SQLstore(IDatabase):
    def __init__(self):
        # Configure logging
        logging.basicConfig(level=logging.DEBUG)

        # Create a logger
        self.logger = logging.getLogger('SQLstore')

        # Create file and console handlers with a formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        self.__sqlconnect = None

        for handler_type in [logging.FileHandler, logging.StreamHandler]:
            handler = handler_type('db.log') if handler_type == logging.FileHandler else handler_type()
            handler.setLevel(logging.INFO if handler_type == logging.FileHandler else logging.DEBUG)
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)


    @property
    def get_connection(self):
        """function to check the connection"""
        return self.__sqlconnect

    def create_connection(self):
        
        """Private function to create connection"""

        try:  
            
            self.__sqlconnect=sqlite3.connect('sql.db')
            self.logger.info(f"Connection created successfully")

        except sqlite3.Error as e:
            self.logger.error(f"Error occured while creating connection: {e}")


    def create_table(self):
        """create a table inside the SQLite DB"""

        try:
            if self.__sqlconnect != None:
                # base case
                if  table_or_not := self.__sqlconnect.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='task'").fetchone():
                    return self.logger.info(f"Table already exists")
                
                self.__sqlconnect.execute('''CREATE TABLE task(
                    DATETIME TEXT, TASK_ID TEXT PRIMARY KEY, TASK_INPUT TEXT
                )''')
                self.logger.info(f"Table created successfully")
            
            else:
                self.logger.info(f"Connection to DB not found")

        except sqlite3.Error as e:
            self.logger.error(f"Error occured in DB: {e}")
            

    def create_task(self,task):
        """creates a task by assigning it unique id and datetime"""
        try:
            meta_data=task_formatter(task)

            assert isinstance(meta_data,dict),f"data should be in dict not {type(meta_data)} "
            assert all(key in meta_data for key in ['DATETIME', 'TASK_ID', 'TASK_INPUT']), "data should have DATETIME, TASK_ID, and TASK_INPUT keys"  # verifying keys

            if self.__sqlconnect != None:
                self.__sqlconnect.execute('''INSERT INTO task (DATETIME, TASK_ID, TASK_INPUT)
                VALUES(?,?,?)

                ''', (meta_data['DATETIME'],meta_data['TASK_ID'],meta_data['TASK_INPUT']))

                self.__sqlconnect.commit()
                self.logger.info(f"Task_id:{meta_data['TASK_ID']} Task_input:{meta_data['TASK_INPUT']} created at:{meta_data['DATETIME']}")
            
            else:
                self.logger.info(f"Connection to DB not found")
        except sqlite3.Error as e :
            self.logger.error(f'Error occurred in DB while inserting: {e}')





    def delete_task(self):
        pass

    def get_all_tasks(self):
        return self.__sqlconnect.execute('''SELECT * FROM task''').fetchall()
        

    def update_task(self):
        pass

    def get_task(self):
        pass

    

db= SQLstore()
# print(db.create_connection())
# db.create_table()
if db.get_connection != None:

    db.create_task('create a file names hello.txt')
    db.create_task('create a file names saf.txt')
    db.create_task('create a file names test.txt')
    db.get_all_tasks()
else:
    db.create_connection()
    db.create_task('create a file names hello.txt')
    db.create_task('create a file names saf.txt')
    db.create_task('create a file names test.txt')
    print(db.get_all_tasks())
