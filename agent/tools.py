import json
import os

import time
from openai import OpenAI
import google.generativeai as genai

from prompts.prompt_handler import PromptHandler

def read_file(file_path=None):
    output_dir = "output"
    full_path = os.path.join(output_dir, file_path)

    # print(f"Function_name: read_file , args: file_path: {full_path}")

    try:
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        if not os.path.exists(full_path):
            raise FileNotFoundError(f"File {full_path} does not exist")

        if full_path.endswith(".txt") or full_path.endswith(".md"):  # Added support for .md files
            with open(full_path, "r") as file:
                data = file.read()
        elif full_path.endswith(".json"):
            with open(full_path, "r") as file:
                data = json.load(file)
        else:
            raise ValueError("Unsupported file format")

        return {"data": data}
    except Exception as e:
        print(f"Error reading file: {e}")
        return {"data": None}


def content_writer(topic):
    
    system_prompt = f"""
    You are a specialized writing assistant. Your task is to create a comprehensive, well-structured report on a given topic. The report should begin with an introduction that clearly states the topic and its significance. Follow this with a background section that provides historical context or foundational information. Then discuss current trends, notable challenges, key stakeholders, and any recent developments relevant to the topic.
    As you compose the report, use clear and concise language, logical organization, and accurate facts. Incorporate headings and subheadings to break down the information into easily digestible sections. Support your points with examples, data, or credible references where possible.
    Conclude the report with a concise summary of key insights, potential solutions or recommendations, and areas where further research or action may be needed. Ensure the tone is professional, informative, and neutral.
    Your overall goal is to deliver a report that is both informative and accessible to a reader who may be new to the subject.
    Stick to the topic at all times.
    Your Topic is:
    {topic}
    """
    model = genai.GenerativeModel(
                    model_name="gemini-1.5-flash",
                    system_instruction=system_prompt)

    response = model.generate_content(
                topic,
            )

    return {"data": response.text}


def conversation_agent(response=None, agent_name=None, task_id=None):
    client = OpenAI(api_key="")
    prompt = PromptHandler()
    convo_template = f"""You are a conversation expert engaged in dialogue with another conversation expert on a specific topic. Your goal is to exchange meaningful information and insights while ensuring the quality and flow of the conversation. 
        Your Name is {agent_name}
        For each response you provide, you will have two options:
        1. **Stop the Conversation**: When you feel the topic has been exhausted, no longer productive, or has reached a satisfying conclusion, you can end the conversation by calling the `stop_conversation` tool. 
        2. **Continue the Conversation**: If new points are to be made or questions need answering, use the `send_message` tool to pass on your response to prompt a reply from the other agent.
        3. **Dont sound robotic** talk in a friendly way like cheerful humans.
        You Have the following agents you can talk with:
        - you cannot talk to yourself, always talk to other agent, make sure you talk to all agents so no one is left behind.
        [alice,bob]
        # Steps

        1. **Analyze the Previous Message**: Evaluate the content of the other expert's response. Identify any questions, new hypotheses, contradictions, or information gaps.
        2. **Construct a Response**:
        - **Insightful Commentary**: Respond thoughtfully by expanding on statements, adding new information, or addressing an open question.
        - **Respectful Tone**: Maintain a tone suitable for a professional expert-level discourse, and avoid redundancy.
        3. **Decide on the Conversation Flow**:
        - If you believe continuing the discussion is productive, use the `send_message` tool and construct a thought-provoking reply.
        - If the conversation seems complete or is no longer viable to move forward meaningfully, call the `stop_conversation` tool.
        
        # Output Format

        - Your response action should include either:
        - A conclusive response (`stop_conversation`). 
        - An insightful continuation (`send_message`) followed by the content of your response.
        
        Indicate clearly which tool you're using:
        - **Use this format**:
        ```send_message```
        [Your response here]

        - **OR**
        ```stop_conversation```

        # Notes

        - Ensure that each response meaningfully contributes to the conversation.
        - Do not artificially prolong dialogues; acknowledge completeness when appropriate.
        - Approach endpoints with clarity—conclude without abruptness and provide closure if stopping.
        ==============================================================================================
        AGENT_RESPONSE:
        {response}

        """
    system_prompt = prompt.get_agent_prompt(
        convo_template, use_history=agent_name, task_id=task_id
    )
    # print("\n\n\n\n", system_prompt, "\n\n\n\n")
    funcs = [
        {
            "type": "function",
            "function": {
                "name": "send_message",
                "description": "Send a message to a specified agent with a query response",
                "strict": True,
                "parameters": {
                    "type": "object",
                    "required": ["agent_name", "from_agent_name", "query_response"],
                    "properties": {
                        "agent_name": {
                            "type": "string",
                            "description": "The name of the agent to send the message to",
                        },
                        "from_agent_name": {
                            "type": "string",
                            "description": "The name of the agent that is sending the message",
                        },
                        "query_response": {
                            "type": "string",
                            "description": "The response message or query to be sent to the agent",
                        },
                    },
                    "additionalProperties": False,
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "stop",
                "description": "Stops the current operation or execution.",
                "strict": True,
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "additionalProperties": False,
                },
            },
        },
    ]
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
        ],
        tools=funcs,
        parallel_tool_calls=True,
        response_format={"type": "text"},
    )

    return {"response": completion, "agent_name": agent_name}


def conversation_agent2(topic, response):
    print(
        {"response": f"conversation_agent2 {topic} I am doing good  {response}"},
    )
    time.sleep(2)
    return {"response": "I am doing good"}


def write_file(file_path=None, data=None):
    output_dir = "output"
    full_path = os.path.join(output_dir, file_path)

    try:
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        with open(full_path, "w") as file:
            if isinstance(data, dict):
                # Write JSON data if it's a dictionary
                json.dump(data, file)
            else:
                # Write as plain text otherwise
                file.write(data)

        message = "File written successfully"
    except Exception as e:
        message = f"Error writing file: {e}"

    # print(f"Function_name: write_file , args: file_path: {full_path}, data: `{data}` ")
    return {"message": message}


