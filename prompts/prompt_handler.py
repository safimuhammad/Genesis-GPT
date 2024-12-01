from string import Template
import json
import logging
from .helpers import format_filename
from .model_logger import initiate_logging
import sqlite3
from storage.database import SQLstore
from storage.agent_memory import AgentMemory


class PromptHandler:
    def __init__(self, file_path=None, use_txt_loader=False):
        """Load file on class initialization and validate it"""
        self.logger = logging.getLogger("PromptHandler")
        # Disable DEBUG logs from httpcore and httpx
        logging.getLogger("httpcore").setLevel(logging.WARNING)
        logging.getLogger("httpx").setLevel(logging.WARNING)
        logging.getLogger("openai._base_client").setLevel(logging.WARNING)
        stream_handler, file_handler = initiate_logging()
        self.logger.addHandler(stream_handler)
        self.logger.addHandler(file_handler)
        self.logger.setLevel(logging.INFO)
        # self.logger.info("PromptHandler initialized")

        if file_path and use_txt_loader is False:
            self.base_prompt = self._load_json_file(file_path)["base_prompt"]

        elif file_path is None and use_txt_loader is False:
            self.base_prompt = self._load_json_file(
                "prompts/prompt_schema/planning_prompt.json"
            )["base_prompt"]

        elif file_path is None and use_txt_loader is True:
            self.base_prompt = self._load_txt_file(
                "prompts/prompt_schema/message_prompt.txt"
            )

    def _load_json_file(self, file_path):
        with open(file_path, "r") as f:
            try:
                data = json.load(f)
                # self.logger.info(
                #     f"file name: {format_filename(file_path)} loaded successfully."
                # )
                return data

            except ValueError as e:
                self.logger.error("invalid json")
                raise

            except FileNotFoundError as e:
                self.logger.error("File does not exist")
                raise

    def _load_txt_file(self, file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            try:
                data = f.read()
                self.logger.info(
                    f"file name: {format_filename(file_path)} loaded successfully."
                )
                return data

            except ValueError as e:
                self.logger.error("invalid json")
                raise

            except FileNotFoundError as e:
                self.logger.error("File does not exist")
                raise

    def add_user_prompt(self, prompt):
        assert isinstance(prompt, str), "Only type str allowed in user prompts"

        prompt_temp = Template(f"""{self.base_prompt}""")
        substituted_prompt = prompt_temp.substitute(
            task=prompt, abilities=self._fetch_abilities()
        )
        self.logger.info("Prompt Template updated with user prompt.")

        return substituted_prompt, prompt

    def experimental_chat_prompt(self, prompt):
        """experimental chat prompt for user alignment"""

        with open("prompts/prompt_schema/chat_prompt.txt", "r") as f:
            base_prompt = f.read()

        prompt_temp = Template(f"""{base_prompt}""")
        substituted_prompt = prompt_temp.substitute(abilities=self._fetch_abilities())

        self.logger.info("Prompt Template updated with chat prompt.")
        return substituted_prompt, prompt

    def sub_vars(self, **kwargs):
        pass

    def _fetch_abilities(self):
        """auto fetch global abilities and substitute in prompt_temp"""

        load_abilities = self._load_json_file("prompts/prompt_schema/abilities.json")

        return load_abilities["abilities"]

    def combine_prompts(self):
        """Combine prompts in base template"""
        pass

    def get_agent_history(self, agent_name, task_id):
        try:
            db = AgentMemory()
            memory = db.fetch_agent_history(agent_name, task_id)
            return memory
        except Exception as e:
            self.logger.info("Error in fetching history: {e}")

    def get_agent_prompt(self, user_prompt, use_history=None, task_id=None):
        if use_history:
            prompt_temp = Template(
                "USER PROMPT:\n $user_prompt \n ```use history for context of previous messages``` AGENT_HISTORY:\n $history"
            )
            return prompt_temp.substitute(
                user_prompt=user_prompt,
                history=self.get_agent_history(use_history, task_id),
            )
        else:
            prompt_temp = Template("USER PROMPT:\n $user_prompt \n")
            return prompt_temp.substitute(user_prompt=user_prompt)
