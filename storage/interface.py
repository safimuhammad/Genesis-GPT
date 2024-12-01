from abc import ABCMeta, abstractstaticmethod, abstractmethod


class IDatabase(metaclass=ABCMeta):

    @abstractmethod
    def add_task(self, task):
        """Adds the task to the database"""
        pass

    @abstractmethod
    def get_task(self, task_id):
        """Gets the task using task id"""
        pass

    @abstractmethod
    def delete_task(self, task_id):
        """Deletes the task using task id"""
        pass

    @abstractmethod
    def update_task(self, task_id, new_task):
        """Updates the task based on task id"""
        pass

    @abstractmethod
    def get_all_tasks(self):
        """Gets all the tasks created by instance"""
        pass
