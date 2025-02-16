# Gemini.py
from .interface import IModel  # Assuming this interface exists
import logging
import google.generativeai as genai
from .model_logger import initiate_logging
from termcolor import colored
from storage.database import SQLstore
import json
from .model_functions import lgtm, error_found
from typing import Optional, Dict, Any
import re

class GeminiAIBrain(IModel):
    # Precompile regex for JSON extraction
    JSON_CODE_BLOCK_REGEX = re.compile(r"```(?:json)?\s*([\s\S]*?)```", re.MULTILINE)

    def __init__(self, model: str, api_key: str):
        self.model = model
        self.logger = logging.getLogger("GeminiAIBrain")
        stream_handler, file_handler = initiate_logging()
        self.logger.addHandler(stream_handler)
        self.logger.addHandler(file_handler)
        self.logger.setLevel(logging.DEBUG)
        
        self.__api_key = None
        self.api_key(api_key)
        self.logger.info(f"GeminiAIBrain model: {model}")

        # Cache model configuration objects for reuse
        self.model_config = None
        self.chat_config = None
        self.__task_id = None
        
        self.db = SQLstore()

    @property
    def api_key_status(self) -> bool:
        if self.__api_key is None:
            self.logger.error("GeminiAIBrain API KEY not set.")
            return False
        self.logger.info("GeminiAIBrain API KEY is set.")
        return True

    def api_key(self, api_key: str) -> None:
        self.__api_key = api_key
        genai.configure(api_key=self.__api_key)
        self.logger.info("GOOGLE_API_KEY set.")

    # Deprecated method remains unchanged
    def llm_completion_deprecated(self, prompt, tool):
        try:
            prompt, user_prompt = prompt
            task_id = self.db.add_task(user_prompt)
            self.client = genai.GenerativeModel(self.model, tools=[tool])
            completion = self.client.generate_content(
                prompt,
                tool_config={"function_calling_config": "ANY"},
            )
            parsed_output = self.parse_llm_output(completion)
            self.db.add_task_plan(task_id, parsed_output)
            self._display(completion)
            return parsed_output
        except Exception as ai_error:
            self.logger.error(f"AIPlatformError: {ai_error}")

    def chat_completion(self, user_prompt: Optional[str] = None, sys_prompt: Optional[str] = None) -> Optional[Dict[str, Any]]:
        try:
            if self.model_config is None:
                self.model_config = genai.GenerativeModel(
                    model_name=self.model,
                    system_instruction=sys_prompt
                )
            if self.chat_config is None:
                self.chat_config = self.model_config.start_chat(
                    enable_automatic_function_calling=True
                )
            if self.__task_id is None and sys_prompt:
                system_task = {"payload": sys_prompt, "type": "SYSTEM_PROMPT"}
                self.__task_id = self.db.add_task(system_task)
            if user_prompt:
                user_task = {"payload": user_prompt, "type": "USER_PROMPT"}
                sub_task_id = self.db.add_task(user_task)
                response = self.chat_config.send_message(user_prompt)
                parsed_response = self.extract_json(response.text)
                response_task = {"payload": parsed_response, "type": "MODEL_RESPONSE"}
                self.db.add_task(response_task, sub_task_id)
                return parsed_response
        except Exception as ai_error:
            self.logger.error(f"Error in chat completion: {ai_error}")
            return {"error": str(ai_error)}

    def extract_json(self, text: str) -> Dict[str, Any]:
        try:
            matches = GeminiAIBrain.JSON_CODE_BLOCK_REGEX.findall(text)
            if matches:
                for match in matches:
                    try:
                        cleaned_json = match.strip()
                        return json.loads(cleaned_json)
                    except json.JSONDecodeError:
                        continue
            text = text.strip()
            if text.startswith("{") and text.endswith("}"):
                try:
                    return json.loads(text)
                except json.JSONDecodeError:
                    # Attempt to clean up common formatting issues
                    import re
                    cleaned_text = re.sub(r"'([^']*)':", r'"\1":', text)
                    cleaned_text = re.sub(r":\s*'([^']*)'", r': "\1"', cleaned_text)
                    return json.loads(cleaned_text)
            return {"response": text}
        except Exception as e:
            self.logger.warning(f"JSON parsing failed, returning text as response: {e}")
            return {"response": text}

    def feedback_agent(self, sys_prompt, user_prompt):
        model_config_2 = genai.GenerativeModel(
            model_name="gemini-2.0-flash-exp",
            system_instruction=sys_prompt,
            tools=[lgtm, error_found],
        )
        chat_config_2 = model_config_2.start_chat(enable_automatic_function_calling=False)
        response = chat_config_2.send_message(user_prompt)
        return response.text

    def parse_llm_output(self, llm_output):
        parsed_output = type(llm_output.candidates[0].content.parts[0]).to_dict(
            llm_output.candidates[0].content.parts[0]
        )["function_call"]["args"]
        return parsed_output

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

            for key, ability in enumerate(format_response["ability"][0]["ability_name"]):
                self.logger.info(
                    f"{bold_start}{italic_start}{colored(f'Tool_to_use: {key} - ','blue')} {bold_end}{italic_end} {italic_start}{colored(ability['tool_to_use']+'()','blue')}{italic_end}"
                )
                self.logger.info(
                    f"{bold_start}{italic_start}{colored(f'Plan_for_tool: {key} - ','cyan')}{bold_end}{italic_end} {italic_start}{colored(ability['plan_for_tool'],'cyan')}{italic_end}"
                )
                self.logger.info(
                    f"{bold_start}{italic_start}{colored(f'args: {key} - ','cyan')}{bold_end}{italic_end} {italic_start}{colored(ability['args'],'cyan')}{italic_end}"
                )
        except Exception as e:
            self.logger.error(f"Error in displaying response: {e}")