# prompt_handler.py
from string import Template
import json
import logging
from .helpers import format_filename
from .model_logger import initiate_logging
import os
from storage.agent_memory import AgentMemory

class PromptHandler:
    def __init__(self, file_path=None, use_txt_loader=False):
        self.logger = logging.getLogger("PromptHandler")
        # Suppress verbose logging from external libraries
        logging.getLogger("httpcore").setLevel(logging.WARNING)
        logging.getLogger("httpx").setLevel(logging.WARNING)
        logging.getLogger("openai._base_client").setLevel(logging.WARNING)
        stream_handler, file_handler = initiate_logging()
        self.logger.addHandler(stream_handler)
        self.logger.addHandler(file_handler)
        self.logger.setLevel(logging.INFO)

        if file_path and not use_txt_loader:
            self.base_prompt = self._load_json_file(file_path)["base_prompt"]
        elif file_path is None and not use_txt_loader:
            self.base_prompt = self._load_json_file(
                os.path.join(os.path.dirname(__file__), "prompt_schema/planning_prompt.json")
            )["base_prompt"]
        elif file_path is None and use_txt_loader:
            prompt_txt = self._load_txt_file(
                os.path.join(os.path.dirname(__file__), "prompt_schema/Multi_Turn_Prompt_With_Dependencies.txt")
            )
            prompt_temp = Template(prompt_txt)
            abilities_str = json.dumps(self._fetch_abilities(), indent=4)
            substituted_prompt = prompt_temp.substitute(abilities=abilities_str)
            self.base_prompt = substituted_prompt

    @property
    def get_system_prompt(self):
        return self.base_prompt

    def _load_json_file(self, file_path):
        with open(file_path, "r") as f:
            try:
                data = json.load(f)
                return data
            except ValueError as e:
                self.logger.error("Invalid JSON in file")
                raise
            except FileNotFoundError as e:
                self.logger.error("File does not exist")
                raise

    def _load_txt_file(self, file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            try:
                data = f.read()
                self.logger.info(f"File name: {format_filename(file_path)} loaded successfully.")
                return data
            except Exception as e:
                self.logger.error("Error reading text file")
                raise

    def add_user_prompt(self, prompt):
        assert isinstance(prompt, str), "Only type str allowed in user prompts"
        substituted_prompt = Template(self.base_prompt).substitute(task=prompt)
        self.logger.info("Prompt Template updated with user prompt.")
        return substituted_prompt, prompt

    def _fetch_abilities(self):
        load_abilities = self._load_json_file(
            os.path.join(os.path.dirname(__file__), "prompt_schema/abilities.json")
        )
        return load_abilities["abilities"]

    def get_agent_history(self, agent_name, task_id):
        try:
            db = AgentMemory()
            memory = db.fetch_agent_history(agent_name, task_id)
            return memory
        except Exception as e:
            self.logger.info(f"Error in fetching history: {e}")

    def get_agent_prompt(self, user_prompt, use_history=None, task_id=None):
        if use_history:
            prompt_temp = Template(
                "USER PROMPT:\n $user_prompt \n ```use history for context of previous messages``` AGENT_HISTORY:\n $history"
            )
            history = self.get_agent_history(use_history, task_id)
            return prompt_temp.substitute(user_prompt=user_prompt, history=history)
        else:
            prompt_temp = Template("USER PROMPT:\n $user_prompt \n")
            return prompt_temp.substitute(user_prompt=user_prompt)