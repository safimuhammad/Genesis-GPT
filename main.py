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
        "data.txt has a topic on which i want to write a blog on and save it to file demo.txt"
    ),
    call_ability,
)

node_metadata = type(test_brain.candidates[0].content.parts[0]).to_dict(
    test_brain.candidates[0].content.parts[0]
)["function_call"]["args"]

graph = Graph(node_metadata)
executor = GraphExecutor(graph.get_graph)
executor.execute_node(0)
