from string import Template
import json
import logging
from .helpers import format_filename
from .model_logger import initiate_logging


class PromptHandler:
    def __init__(self, file_path=None, use_txt_loader=False):
        """Load file on class initialization and validate it"""
        self.logger = logging.getLogger("PromptHandler")
        stream_handler, file_handler = initiate_logging()
        self.logger.addHandler(stream_handler)
        self.logger.addHandler(file_handler)
        self.logger.setLevel(logging.DEBUG)
        self.logger.info("PromptHandler initialized")

        if file_path and use_txt_loader is False:
            self.base_prompt = self._load_json_file(file_path)["base_prompt"]

        elif file_path is None and use_txt_loader is False:
            self.base_prompt = self._load_json_file("prompts/planning_prompt.json")[
                "base_prompt"
            ]

        elif file_path is None and use_txt_loader is True:
            self.base_prompt = self._load_txt_file("prompts/planning_prompt.txt")

    def _load_json_file(self, file_path):
        with open(file_path, "r") as f:
            try:
                data = json.load(f)
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

    def _load_txt_file(self, file_path):
        with open(file_path, "r") as f:
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

        return substituted_prompt

    def _fetch_abilities(self):
        """auto fetch global abilities and substitute in prompt_temp"""

        load_abilities = self._load_json_file("prompts/abilities.json")

        return load_abilities["abilities"]

    def combine_prompts(self):
        """Combine prompts in base template"""
        pass
