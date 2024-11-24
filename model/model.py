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


# ==================================================== Ignore below this line ==================================================
ai = OpenAIBrain(model="gpt-4-0125-preview")
prompt_temp = Template(
    """
                    Goals: List  goals that the expert aims to achieve in order to help with the task
                    You should always have your thoughts laid out first, then reason with it and carefully lay out your plan with you abilities in mind.

                    Your task is:
                    Lets work this out in a step by step way to be sure we have the right answer.
                    $task

        
                    Answer in the provided format.
                    Your decisions must be made independently without seeking user assistance. Play with your strengths as an LLM and pursue simple strategies.

                    You have access to the following abilities you can call:
                    - write_file()
                    - read_file()  
                    
                """
)

prompt = prompt_temp.substitute(
    task="copy the text in file safi.txt and paste it into new file named test.txt"
)
functions = [
    {
        "name": "planning_llm_output",
        "description": "Structure the output from llm.",
        "parameters": {
            "type": "object",
            "properties": {
                "thoughts": {
                    "type": "object",
                    "description": "recieves object consisting of text,reasoning,plan,criticism, speak",
                    "properties": {
                        "text": {
                            "type": "string",
                            "description": "Your thoughts on the task",
                        },
                        "reasoning": {
                            "type": "string",
                            "description": "reasoning behind thoughts.",
                        },
                        "plan": {
                            "type": "string",
                            "description": "short bulleted\\n- list that conveys\\n- long-term plan",
                        },
                        "criticism": {
                            "type": "string",
                            "description": "constructive self-criticism",
                        },
                        "speak": {
                            "type": "string",
                            "description": "thoughts summary to say to user",
                        },
                    },
                },
                "ability": {
                    "type": "object",
                    "description": "recieves name of abilities that are relevant to the task.",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "single or multiple ability names",
                        }
                    },
                },
            },
            "required": ["thoughts", "ability"],
        },
    }
]
print(ai.llm_completion(prompt, functions))
