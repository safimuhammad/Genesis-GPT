import json

def lgtm(next_agent_message: str):
    """
    Looks good to me, no action to current output, execute the next agent.

    Args:
        next_agent_message (str): A JSON string describing the next agent message.
            Example (as a raw string):
                "{
                  \"from_agent\": \"master_agent\",
                  \"to_agent\": \"read_file\",
                  \"message\": \"Read the contents of demo.txt.\",
                  \"args\": [
                    {
                      \"arg_name\": \"file_path\",
                      \"arg_value\": \"demo.txt\",
                      \"is_static\": true
                    }
                  ]
                }"

    Returns:
        str: A JSON string that wraps the original next_agent_message as an object, for example:
            "{
              \"next_agent_message\": {
                \"from_agent\": \"master_agent\",
                \"to_agent\": \"read_file\",
                ...
              },
              function_name (str): The name of the function called.

            }"
    """
    # 1. Parse the JSON string into a dictionary
    msg_dict = json.loads(next_agent_message)

    # 2. Build your result dictionary
    result_dict = {"next_agent_message": msg_dict,"function_name": "lgtm"}

    # 3. Return it as a JSON string
    return json.dumps(result_dict)


def error_found(corrected_agent_message: str, correction: str):
    """
    Error found in the output, re-execute with correction.

    Args:
        corrected_agent_message (str): A JSON string describing the corrected agent message.
            Example (as a raw string):
                "{
                  \"from_agent\": \"master_agent\",
                  \"to_agent\": \"read_file\",
                  \"message\": \"Read the contents of demo.txt.\",
                  \"args\": [
                    {
                      \"arg_name\": \"file_path\",
                      \"arg_value\": \"demo.txt\",
                      \"is_static\": true
                    }
                  ]
                }"
        correction (str): Suggested correction for the agent.

    Returns:
        str: A JSON string that wraps the original failed_agent_message and a correction, for example:
            "{
              \"failed_agent_message\": {
                \"from_agent\": \"master_agent\",
                \"to_agent\": \"read_file\",
                ...
              },
              \"correction\": \"Your correction string\",
            function_name (str): The name of the function called.

            }"
    """
    # 1. Parse the JSON string into a dictionary
    failed_dict = json.loads(corrected_agent_message)

    # 2. Build a Python dictionary containing the needed data
    result_dict = {
        "corrected_agent_message": failed_dict,
        "correction": correction,
        "function_name": "error_found"
    }
    # 3. Return it as a JSON string
    return json.dumps(result_dict)