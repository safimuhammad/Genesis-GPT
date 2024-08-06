from model.gemini import GeminiAIBrain
from prompts.prompt_handler import PromptHandler
from prompts.gemini_schema import call_ability
import json


# work in progress
class WorkflowBuilder:
    def __init__(self, api_key, use_txt_loader):
        """Orchestrate all components to work together"""
        self.__api_key = api_key
        self.__use_txt_loader = use_txt_loader
