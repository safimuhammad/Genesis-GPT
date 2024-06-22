from .interface import IModel  # relative imports
import logging
import os
import google.generativeai as genai
from string import Template
from .model_logger import initiate_logging


class GeminiAIBrain(IModel):
    def __init__(self, model, api_key):
        """Initializing logging and api key"""
        self.model = model
        self.logger = logging.getLogger("GeminiAIBrain")
        stream_handler, file_handler = initiate_logging()
        self.logger.addHandler(stream_handler)
        self.logger.addHandler(file_handler)
        self.logger.setLevel(logging.DEBUG)
        self.api_key(api_key)
        self.logger.info(f"GeminiAIBrain model: {model}")

    @property
    def api_key_status(self):
        """Check the status of API key"""
        if self.__api_key == None:
            self.logger.error(f"GeminiAIBrain API KEY not set.")
        else:
            self.logger.info(f"GeminiAIBrain API KEY already set.")

        return self.__api_key

    def api_key(self, api_key):
        """Set API key"""
        self.__api_key = api_key
        genai.configure(api_key=self.__api_key)
        self.logger.info("GOOGLE_API_KEY API KEY set.")

    def llm_completion(self, prompt, tool):
        try:
            self.client = genai.GenerativeModel(self.model, tools=[tool])
            completion = self.client.generate_content(
                prompt,
                # Force a function call
                tool_config={"function_calling_config": "ANY"},
            )

            return completion

        except Exception as ai_error:
            self.logger.error(f"AIPlatformError: {ai_error}")
