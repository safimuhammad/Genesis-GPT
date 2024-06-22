import logging
import os
from string import Template
from openai import OpenAI
from model_logger import initiate_logging
import ollama
import json
from string import Template
from schema import ExecutionOrder
import instructor


class TaskHandler:
    def __init__(self, model: str, use_pydantic: bool = False):
        self._model = model
        self.logger = logging.getLogger("TaskHandler")
        stream_handler, file_handler = initiate_logging()
        self.logger.addHandler(stream_handler)
        self.logger.addHandler(file_handler)
        self.logger.setLevel(logging.DEBUG)
        self.logger.info(f"TaskHandler model: {self._model}")

        if use_pydantic:
            self._client = instructor.from_openai(
                OpenAI(
                    base_url="http://localhost:11434/v1",
                    api_key="ollama",  # required, but unused
                ),
                mode=instructor.Mode.JSON,
            )

    def load_prompt(self, task):
        with open("./prompts/task_handler_prompt.txt", "r") as f:
            prompt = f.read()

        load_input = Template(prompt)
        return self.generate_prompt(load_input, task)

    def generate_prompt(self, template, task):
        prompt = template.substitute(task=task)
        return prompt

    def raw_completion(self, task):
        instructions = self.load_prompt(task)
        completion = ollama.generate(
            model=self._model,
            prompt=instructions,
        )
        return completion["response"]

    def pydantic_completion(self, task):

        if self._client is None:
            return self.logger.error(
                f"TaskHandler Error: Ollama client not initialized"
            )
        instructions = self.load_prompt(task)
        print(instructions)

        try:
            response = self._client.chat.completions.create(
                model=self._model,
                messages=[
                    {
                        "role": "system",
                        "content": instructions,
                    }
                ],
                response_model=ExecutionOrder,
            )
            response_dict = response.dict()
            self.logger.info(f"TaskHandler output: {response_dict}")
            return response_dict

        except Exception as e:
            self.logger.error(f"TaskHandler error: {e}")
