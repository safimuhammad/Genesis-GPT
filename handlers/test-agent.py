import ollama
from openai import OpenAI
from pydantic import BaseModel, Field
from typing import List
import instructor
from schema import ExecutionOrder
from task_handler import TaskHandler
import json

task_handler = TaskHandler("llama3", use_pydantic=True)

task_3 = {
    "previous_agents_output": [None],
    "thoughts": [
        {
            "criticism": [],
            "planning": [
                "To copy content from test.txt to production.txt we need to follow two steps:\\n1. Read the content from the test.txt file.\\n2. Write the content to a new file production.txt."
            ],
        }
    ],
    "ability": [
        {
            "ability_name": [
                {
                    "tool_to_use": "read_file",
                    "plan_for_tool": "First, we need to read the contents of the file named 'test.txt' using the read_file tool, and store it in a variable called 'content'.",
                },
                {
                    "tool_to_use": "write_file",
                    "plan_for_tool": "Then, we need to create a new file named 'production.txt' and write the content stored in 'content' variable to it using the write_file tool.",
                },
            ]
        }
    ],
}

task_4 = {
    "previous_agents_output": [{"read_file": "Hello world!!!"}],
    "thoughts": [
        {
            "criticism": [],
            "planning": [
                "To process data from data.csv and save the results to results.csv, we need to follow three steps:\n1. Read the data from the data.csv file.\n2. Process the data to compute necessary results.\n3. Write the processed results to a new file results.csv."
            ],
        }
    ],
    "ability": [
        {
            "ability_name": [
                {
                    "tool_to_use": "read_file",
                    "plan_for_tool": "First, we need to read the contents of the file named 'data.csv' using the read_file tool and store it in a variable called 'data'.",
                },
                {
                    "tool_to_use": "process_data",
                    "plan_for_tool": "Next, we need to process the 'data' variable to compute the necessary results and store the output in a variable called 'processed_data'.",
                },
                {
                    "tool_to_use": "write_file",
                    "plan_for_tool": "Finally, we need to create a new file named 'results.csv' and write the 'processed_data' to it using the write_file tool.",
                },
            ]
        }
    ],
}

print(task_handler.pydantic_completion(task_4))
