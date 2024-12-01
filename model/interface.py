from abc import ABCMeta, abstractstaticmethod ,abstractmethod,abstractclassmethod

class IModel(metaclass=ABCMeta):

    @abstractmethod
    def llm_completion(self,prompt):
        """Makes a call to llm for completion"""
        pass

    