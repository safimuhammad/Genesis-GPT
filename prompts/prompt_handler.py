from string import Template
import json
import logging
from helpers import format_filename
from model_logger import initiate_logging

class PromptHandler():
    def __init__(self,file_path):
        """Load file on class initialization and validate it"""
        self.logger= logging.getLogger('PromptHandler')
        self.__handler=initiate_logging()
        self.logger.addHandler(self.__handler)
        self.logger.info("PromptHandler initiated")
        self.base_prompt= self.load_file(file_path)['base_prompt']

        
    def load_file(self,file_path):
        with open(file_path,'r') as f:
            try:
                data = json.load(f)
                self.logger.info(f"file name: {format_filename(file_path)} loaded successfully.")
                return data

            except ValueError as e:
                self.logger.error('invalid json')
                raise

            except FileNotFoundError as e:
                self.logger.error('File does not exist')
                raise

    def add_user_prompt(self,prompt):
        assert isinstance(prompt,str), 'Only type str allowed in user prompts'

        prompt_temp = Template(f"""{self.base_prompt}""")
        substituted_prompt = prompt_temp.substitute(task=prompt,abilities='hk')
        self.logger.info('Prompt Template updated with user prompt.')

        return substituted_prompt

    def fetch_abilities(self):
        """auto fetch global abilities and substitute in prompt_temp"""
        pass

    def combine_prompts(self):
        """Combine prompts in base template"""
        pass


foo=PromptHandler('prompts/planning_prompt.json')
foo.add_user_prompt('hel')