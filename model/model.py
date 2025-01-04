from interface import IModel
import logging
import os
from openai import OpenAI
import openai
from string import Template


class OpenAIBrain(IModel):
    def __init__(self, model):
        """Initializing logging and api key"""
        self.__api_key = None
        self.model = model

        logging.basicConfig(level=logging.DEBUG)
        self.logger = logging.getLogger("OpenAIBrain")
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        for handler_type in [logging.FileHandler, logging.StreamHandler]:
            handler = (
                handler_type("model.log")
                if handler_type == logging.FileHandler
                else handler_type()
            )
            handler.setLevel(
                logging.INFO if handler_type == logging.FileHandler else logging.DEBUG
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

    @property
    def api_key(self):
        """Check the status of API key"""
        if self.__api_key == None:
            self.logger.error(f"OpenAI API KEY not set.")
        else:
            self.logger.info(f"OpenAI API KEY already set.")

        return self.__api_key

    @api_key.setter
    def api_key(self, api_key):
        """Set API key"""
        self.__api_key = api_key
        os.environ["OPENAI_API_KEY"] = self.__api_key
        self.logger.info("OpenAI API KEY set.")

    def llm_completion(self, prompt, tool):
        try:
            self.client = OpenAI()
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Think as an expert"},
                    {"role": "user", "content": prompt},
                ],
                functions=tool,
                function_call={"name": "planning_llm_output"},
            )
            return completion

        except openai.AuthenticationError as e:
            self.logger.error(f"Authentication Error: {e}")

        except openai.BadRequestError as e:
            self.logger.error(f"Invalid Request Error: {e}")

        except openai.RateLimitError as e:
            self.logger.error(f"Rate Limit Error: {e}")


