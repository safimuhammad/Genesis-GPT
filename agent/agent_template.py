import logging
from termcolor import colored
import importlib
import json
import os
import sys
import inspect


class Agent:
    def __init__(self, node_metadata, next_ability, logger):
        """Agent template for tools"""
        self.logger = logger
        self.node_no = node_metadata["node_no"]
        self.tool_to_use = node_metadata["tool_to_use"]
        self.plan_for_tool = node_metadata["plan_for_tool"]
        self.args = self.parse_args(node_metadata["args"])
        self.next_ability = node_metadata["next_ability"]

        self.logger.info(f"{colored(f'Agent: {self.tool_to_use}','magenta')}")

        # properties to set
        self.next_agent_cls = None

        # Import current function
        self.func = self.import_ability(self.tool_to_use)

    def import_ability(self, function_name):
        """import tool"""
        module_path = os.path.abspath(os.path.dirname(__file__))
        if module_path not in sys.path:
            sys.path.insert(0, module_path)

        module_name = "tools"
        module = importlib.import_module(module_name)
        return getattr(module, function_name)

    def execute(self):
        """execute tool"""
        try:
            args = self.args
            output = self.func(**args)
            if self.next_agent_cls:
                next_agent = self.next_agent_cls
                for k, v in output.items():
                    if k in next_agent.args:
                        next_agent.args[k] = v
            return output
        except Exception as e:
            self.logger.error(f"Execution Error: {e}")
            return

    def parse_args(self, args_dict):
        """set args for tool"""
        if args_dict is None:
            return None
        set_args = {arg["arg_name"]: arg["arg_value"] for arg in args_dict}
        return set_args

    def get_next_node(self):
        return self.next_ability[0] if self.next_ability else None

    @property
    def next_agent(self):
        """next agent"""
        return self.next_agent_cls

    @next_agent.setter
    def next_agent(self, val):
        """next agent setter"""
        self.next_agent_cls = val
