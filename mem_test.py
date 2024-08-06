from model.gemini import GeminiAIBrain
from prompts.prompt_handler import PromptHandler
from prompts.gemini_schema import call_ability
import json
from router.graph import Graph
from router.executor import GraphExecutor

# promp = """


# """
# with open("api_key.json", "r") as file:
#     data = json.load(file)
#     gemini_key = data.get("gemini_api_key", None)

# brain = GeminiAIBrain(model="gemini-1.5-pro", api_key=gemini_key)
# test_brain = brain.test_completion("hello")
# print(test_brain)
