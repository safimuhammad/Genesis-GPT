from model.gemini import GeminiAIBrain
from prompts.prompt_handler import PromptHandler
from prompts.gemini_schema import call_ability
import json
from router.graph import Graph
from router.executor import GraphExecutor


with open("api_key.json", "r") as file:
    data = json.load(file)
    gemini_key = data.get("gemini_api_key", None)

brain = GeminiAIBrain(model="gemini-1.5-pro", api_key=gemini_key)
prompt = PromptHandler(use_txt_loader=True)


test_brain = brain.llm_completion(
    prompt.add_user_prompt(
        "do a back and forth conversation between agent1 and agent2 on global warming."
    ),
    call_ability,
)
# print(test_brain)


# test_brain = brain.test_completion(
#     prompt.experimental_chat_prompt("create a function in python to add two integers"),
#     call_ability,
# )
# print(test_brain)


graph = Graph(test_brain)
# print(graph.get_graph)
executor = GraphExecutor(graph.get_graph)
executor.execute_node(0)
