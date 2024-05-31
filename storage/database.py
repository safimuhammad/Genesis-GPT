from interface import IDatabase
import sqlite3
import logging
import uuid
from helpers import task_formatter,connection_handler



class SQLstore(IDatabase):
    def __init__(self):
        """Initializing logging and connections"""

        logging.basicConfig(level=logging.DEBUG)
        self.logger = logging.getLogger('SQLstore')
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
        """function to create connection"""
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
    
    def delete_task(self,task_id):
        """Delete a single task based on task_id"""
        try:
            if self.__sqlconnect != None:
                # base case
                if self.__sqlconnect.execute('SELECT * FROM task WHERE TASK_ID=?',(task_id,)).fetchone():
                    self.__sqlconnect.execute('DELETE FROM task WHERE TASK_ID=?',(task_id,))
                    self.__sqlconnect.commit()
                    self.logger.info(f"task_id: {task_id} deleted successfully")
                else:
                    self.logger.error(f'task: {task_id} does not exist.')
            else:
                self.logger.info(f"Connection to DB not found")


        except sqlite3.Error as e:
            self.logger.error(f"Failed to delete task_id {task_id}: {e}")


    def get_all_tasks(self):
        """Fetches all tasks from the db"""
        return self.__sqlconnect.execute('''SELECT * FROM task''').fetchall()
        

    def update_task(self,task_id,task_input):
        """Updates task based on task_id"""
        try:
            if self.__sqlconnect != None:
                self.__sqlconnect.execute('UPDATE task SET TASK_INPUT=? WHERE TASK_ID=?',(task_input , task_id))
                self.__sqlconnect.commit()
                self.logger.info(f'task_id:{task_id} updated successfully')
            else:
                self.logger.error('Connection to DB not found')
        except sqlite3.Error as e :
            self.logger.error(f'Error updating task_id: {task_id} caused by {e}')


    def get_task(self,task_id):
        """Gets the specific task based on task_id"""
        try:
            if self.__sqlconnect != None:
                task=self.__sqlconnect.execute("SELECT * FROM task WHERE TASK_ID=?",(task_id,)).fetchone()
                
                return task if task else self.logger.error(f'task: {task_id} does not exist')
        except sqlite3.Error as e:
            self.logger.error(f'Error occurred while fetching task_id {task_id} due to: {e}')



    

# db= SQLstore()

# db.create_connection()
# db.delete_task('150e4457-69d4-4707-bb7f-38ab2bb476c5')
    # print(db.get_task('150e4457-69d4-4707-bb7f-38ab2bb476c5'))
    # print(db.get_all_tasks())


