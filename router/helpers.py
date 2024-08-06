def parse_brain_output_v2(result_dict):
    graph = result_dict.get("graph", None)
    node_info_list = []

    for order, plan in enumerate(result_dict["ability"][0]["ability_name"]):
        node = {}
        node["node_no"] = order
        for key in plan.keys():
            node[key] = plan[key]

        node_info_list.append(node)
    return node_info_list


def parse_brain_output_v1(result_dict):
    node_info_list = []
    node_no = 0  # Initialize the node number

    # Iterate through each ability in the ability list
    for ability in result_dict["ability"]:
        for plan in ability["ability_name"]:
            node = {}
            node["node_no"] = node_no  # Assign the current node number
            for key in plan.keys():
                node[key] = plan[key]
            node_info_list.append(node)
            node_no += 1  # Increment the node number for the next ability

    return node_info_list
