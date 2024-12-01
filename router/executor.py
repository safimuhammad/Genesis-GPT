from .model_logger import initiate_logging
from termcolor import colored
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from agent.agent_template import Agent

import logging


class GraphExecutor:
    def __init__(self, node_metadata_list):
        """Executes the individual nodes and their conncted nodes"""

        self.logger = logging.getLogger("Graph Executor")
        stream_handler, file_handler = initiate_logging()
        self.logger.addHandler(stream_handler)
        self.logger.addHandler(file_handler)
        self.logger.setLevel(logging.DEBUG)
        self.nodes = {}
        self.create_nodes(node_metadata_list)
        self.logger.info(f"{colored('Agents Built','blue')}")

    def create_nodes(self, node_metadata_list):
        """creates nodes out of node metadata"""
        for key, node_metadata in enumerate(node_metadata_list):
            next_node = None
            if (key + 1) <= len(node_metadata_list) - 1:
                next_node = node_metadata_list[key + 1]
            node = Agent(node_metadata, next_node, self.logger)
            self.nodes[node.node_no] = node

    @property
    def get_node_metadata_list(self):
        """get node metadata"""
        return self.get_node_metadata_list

    @property
    def get_nodes(self):
        """get nodes"""
        return self.nodes

    def execute_node(self, node_no):
        """execute node and its connected node"""
        try:
            node = self.nodes.get(node_no)
            if node:
                self._set_next_agent(node)
                result = node.execute()
                # Only continue if result is not None and is truthy
                if result:
                    self.logger.info(f"Node {node_no} executed with result: {result}")
                    next_node = node.get_next_node()
                    if next_node:
                        self.execute_node_by_tool(next_node)
                else:
                    self.logger.info(
                        f"Node {node_no} returned an empty or None result. Stopping execution."
                    )
            else:
                self.logger.info(f"Node {node_no} not found.")

        except Exception as e:
            self.logger.error(f"Error executing node {node_no}: {e}")
            sys.exit(1)

            return

    def execute_node_by_tool(self, tool_to_use):
        """execute node by tool_name"""
        try:
            for node in self.nodes.values():
                if node.tool_to_use == tool_to_use:
                    self._set_next_agent(node)
                    result = node.execute()

                    self.logger.info(
                        f"Node with tool {tool_to_use} executed with result: {result}"
                    )
                    next_node = node.get_next_node()
                    if next_node:
                        self.execute_node_by_tool(next_node)
                    break
        except Exception as e:
            self.logger.error(f"Error executing node with tool {tool_to_use}: {e}")
            sys.exit(1)
            return  # Stop execution

    def _set_next_agent(self, node):
        """send next agent class to the current agent"""
        next_node = node.get_next_node()
        if next_node:
            get_index = self.get_node_index(next_node)
            next_agent = self.nodes.get(get_index)
            if next_agent:
                node.next_agent = next_agent

    def get_node_index(self, ability_name):
        """get node no by its name"""
        for node in self.nodes.values():
            if node.tool_to_use == ability_name:
                return node.node_no
