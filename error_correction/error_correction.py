from langchain_experimental.llms.ollama_functions import OllamaFunctions
from langchain_core.messages import HumanMessage, SystemMessage
from model_logger import initiate_logging
from termcolor import colored
import json
import logging


class ErrorCorrection:
    def __init__(self):
        """Error Correction in Agents"""

        self.logger = logging.getLogger("Error Correction")
        stream_handler, file_handler = initiate_logging()
        self.logger.addHandler(stream_handler)
        self.logger.addHandler(file_handler)
        self.logger.setLevel(logging.DEBUG)

        self.model = OllamaFunctions(model="llama3.1", format="json")
        self.model = self.model.bind_tools(tools=self.import_tools)
        self.logger.info(f"{colored('Error Correction: Initialized!','yellow')}")

    @property
    def import_tools(self):
        try:
            with open("tools.json", "r") as f:
                tools = json.load(f)
            return tools
        except Exception as e:
            self.logger.error(f"{colored(f'Error Correction: {e}','red')}")

    def evaluate_error(self, query):
        try:
            response = self.model.invoke(query)
            return response

        except Exception as e:
            self.logger.info(f"error:{e}")


foo = ErrorCorrection()
print(foo.evaluate_error("whats the happening in toronto"))
