from abc import ABCMeta, abstractstaticmethod ,abstractmethod,abstractclassmethod

class IModel(metaclass=ABCMeta):

    @abstractmethod
    def  chat_completion(self,prompt):
        """Makes a call to llm for completion"""
        pass

    