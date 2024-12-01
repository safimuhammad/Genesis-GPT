import importlib
import json


class Node:
    def __init__(self, node_metadata):
        self.node_no = node_metadata["node_no"]
        self.tool_to_use = node_metadata["tool_to_use"]
        self.plan_for_tool = node_metadata["plan_for_tool"]
        self.args = node_metadata["args"]
        self.next_ability = node_metadata["next_ability"]

        # Import the function dynamically
        self.func = self.import_function(self.tool_to_use)

    def import_function(self, function_name):
        # Assuming all functions are in a module named 'tools'
        module_name = "tools"
        module = importlib.import_module(module_name)
        return getattr(module, function_name)

    def execute(self):
        # Prepare arguments
        args = {arg["arg_name"]: arg["arg_value"] for arg in self.args}
        return self.func(**args)

    def get_next_node(self):
        return self.next_ability[0] if self.next_ability else None


class NodeManager:
    def __init__(self, node_metadata_list):
        self.nodes = {}
        self.create_nodes(node_metadata_list)
        print(self.nodes, "created nodes")

    def create_nodes(self, node_metadata_list):
        for node_metadata in node_metadata_list:
            node = Node(node_metadata)
            self.nodes[node.node_no] = node

    def execute_node(self, node_no):
        if node_no in self.nodes:
            node = self.nodes[node_no]
            result = node.execute()
            print(f"Node {node_no} executed with result: {result}")
            next_node = node.get_next_node()
            if next_node:
                self.execute_node_by_tool(next_node)
        else:
            print(f"Node {node_no} not found.")

    def execute_node_by_tool(self, tool_to_use):
        for node in self.nodes.values():
            if node.tool_to_use == tool_to_use:
                result = node.execute()
                print(f"Node with tool {tool_to_use} executed with result: {result}")
                next_node = node.get_next_node()
                if next_node:
                    self.execute_node_by_tool(next_node)
                break


# Example usage:

node_metadata_list = [
    {
        "node_no": 0,
        "tool_to_use": "read_file",
        "plan_for_tool": "Read the content of test.txt",
        "args": [{"arg_name": "file_path", "arg_value": "test.txt", "is_static": True}],
        "next_ability": ["content_writer"],
    },
    {
        "node_no": 2,
        "tool_to_use": "content_writer",
        "plan_for_tool": "Write content to output.txt",
        "args": [
            {
                "arg_name": "prompt",
                "arg_value": "write a report on top 5 smartphones",
                "is_static": True,
            },
        ],
        "next_ability": ["write_file"],
    },
    {
        "node_no": 1,
        "tool_to_use": "write_file",
        "plan_for_tool": "Write content to output.txt",
        "args": [
            {"arg_name": "file_path", "arg_value": "output.txt", "is_static": True},
            {"arg_name": "content", "arg_value": "Hello, World!", "is_static": True},
        ],
        "next_ability": [],
    },
]

# Initialize NodeManager with the list of node metadata
node_manager = NodeManager(node_metadata_list)

# # Execute the first node
node_manager.execute_node(0)

