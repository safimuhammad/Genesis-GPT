from router.graph import Graph
import json
from router.executor import GraphExecutor

with open("output/testv2.json", "r") as f:
    node_metadata = json.load(f)


graph = Graph(node_metadata)
print(graph.get_graph)
executor = GraphExecutor(graph.get_graph)
executor.execute_node(0)
