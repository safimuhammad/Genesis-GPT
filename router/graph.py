from .model_logger import initiate_logging
from termcolor import colored
from .helpers import parse_brain_output_v1, parse_brain_output_v2
import logging


class Graph:
    def __init__(self, brain_output):
        """Creates graph with model output"""
        self.logger = logging.getLogger("Graph")
        stream_handler, file_handler = initiate_logging()
        self.logger.addHandler(stream_handler)
        self.logger.addHandler(file_handler)
        self.logger.setLevel(logging.DEBUG)
        self.graph = {}
        self._node_info = []
        self.graph_with_info = []
        self.logger.info(f"{colored('Graph Initialized','light_magenta')}")

        if brain_output["graph"]:
            self.meta_graph = brain_output["graph"]
            self.create_graph(self.meta_graph)
            self._node_info = parse_brain_output_v1(brain_output)
            if self._node_info:
                self.merge_relation_with_nodes()

            if self.graph_with_info:
                self.logger.info(f"{colored('Nodes connected with edges','yellow')}")

    def add_node(self, node):
        """add node in graph"""
        if node not in self.graph:
            self.graph[node] = []
        else:
            self.logger.error("Node already exists")

    def add_edge(self, node1, node2):
        """connect nodes"""
        if node1 in self.graph and node2 in self.graph:
            self.graph[node1].append(node2)
        else:
            self.logger.error("Graph Error: Nodes does not exist.")

    @property
    def display(self):
        for node in self.graph:
            print(f"{node}: {self.graph[node]}")

    def merge_relation_with_nodes(self):
        """connect all nodes for graph with full data"""
        for node in self._node_info:
            node_data = {
                "node_no": node["node_no"],
                "tool_to_use": node["tool_to_use"],
                "plan_for_tool": node["plan_for_tool"],
                "args": node["args"],
                "next_ability": [],
            }
            for relation in self.meta_graph:
                if relation["ability"] == node["tool_to_use"]:
                    node_data["next_ability"] = relation["next_ability"]
                    break
            self.graph_with_info.append(node_data)

    @property
    def get_graph(self):
        """get the created graph"""
        return self.graph_with_info

    @property
    def get_starting_nodes(self):
        """get starting root nodes"""
        in_degree = {node: 0 for node in self.graph}
        for node in self.graph:
            for neighbor in self.graph[node]:
                in_degree[neighbor] += 1

        starting_nodes = [node for node in in_degree if in_degree[node] == 0]
        return starting_nodes

    def create_graph(self, graph):
        """generate meta graph without all data"""
        assert isinstance(graph, list), "List is required to map nodes"
        try:
            for node in graph:
                self.add_node(node["ability"])
                for edge in node["next_ability"]:
                    self.add_node(edge)
                    self.add_edge(node["ability"], edge)

            self.logger.info(f"{colored('Nodes created','blue')}")

        except Exception as e:
            self.logger.error(f"Graph error: {e}")
