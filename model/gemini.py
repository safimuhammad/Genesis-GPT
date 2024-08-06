from .interface import IModel  # relative imports
import logging
import os
import google.generativeai as genai
from string import Template
from .model_logger import initiate_logging
from termcolor import colored


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
            self._display(completion)

            return completion

        except Exception as ai_error:

            self.logger.error(f"AIPlatformError: {ai_error}")

    def test_completion(self, prompt):
        """Experimental"""
        try:
            self.client = genai.GenerativeModel(self.model)
            completion = self.client.generate_content(
                prompt,
            )
            return completion
        except Exception as e:
            self.logger.error(f"AIPlatformError: {ai_error}")

    def _display(self, response):
        try:

            italic_start = "\033[3m"
            italic_end = "\033[0m"

            bold_start = "\033[1m"
            bold_end = "\033[0m"

            format_response = type(response.candidates[0].content.parts[0]).to_dict(
                response.candidates[0].content.parts[0]
            )["function_call"]["args"]

            for i in format_response["thoughts"]:
                self.logger.info(
                    f"{bold_start}{italic_start}{colored('Criticism:','yellow')} {bold_end}{italic_end} {italic_start}{colored(i['criticism'],'yellow')}{italic_end}"
                )
                for k, j in enumerate(i["planning"]):
                    self.logger.info(
                        f"{bold_start}{italic_start}{colored(f'Planning:{k} - ','magenta')} {bold_end}{italic_end} {italic_start}{colored(j,'magenta')}{italic_end}"
                    )

            for key, ability in enumerate(
                format_response["ability"][0]["ability_name"]
            ):
                self.logger.info(
                    f"{bold_start}{italic_start}{colored(f'Tool_to_use: {key} - ','blue')} {bold_end}{italic_end} {italic_start} {colored(ability['tool_to_use']+'()','blue')}{italic_end}"
                )
                self.logger.info(
                    f"{bold_start}{italic_start}{colored(f'Plan_for_tool: {key} - ','cyan')}{bold_end}{italic_end} {italic_start}{colored(ability['plan_for_tool'],'cyan')}{italic_end}"
                )
                self.logger.info(
                    f"{bold_start}{italic_start}{colored(f'args: {key} - ','cyan')}{bold_end}{italic_end} {italic_start}{colored(ability['args'],'cyan')}{italic_end}"
                )

        except Exception as e:

            self.logger.error(f"error in displaying response: {e}")
