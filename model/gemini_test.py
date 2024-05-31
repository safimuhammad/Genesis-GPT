from gemini import GeminiAIBrain
from string import Template
from typing_extensions import TypedDict
import json 

ai= GeminiAIBrain(model='gemini-1.5-pro',api_key="AIzaSyBcKP5d0a-yZByHAhGO9PFP3A2ypPjkiw8")
prompt_temp= Template("""
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
                    
                """)
prompt= prompt_temp.substitute(task='copy the text in file safi.txt and paste it into new file named test.txt')
class Thoughts(TypedDict):
    planning: list[str]
    criticism: list[str]

class Ability(TypedDict):
    ability_name: list[str]

def call_ability(
    thoughts: list[Thoughts],
    ability: list[Ability]
):
    pass
print(prompt)
result=ai.llm_completion(prompt,call_ability)
# fc = result.candidates[0].content.parts[0].function_call
# print(json.dumps(type(fc).to_dict(fc), indent=4))