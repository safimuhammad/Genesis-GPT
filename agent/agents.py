from .agent_template_v2 import AgentBase
from .tools import read_file, write_file, conversation_agent, content_writer
from prompts.prompt_handler import PromptHandler
import json

import time
from .decorators import add_memory_decorator


class ReadAgent(AgentBase):
    def execute(self):
        kwargs = self.resolve_message()
        result = read_file(**kwargs)
        self.send_output(result)
        print(result)


class WriteAgent(AgentBase):
    def execute(self):
        kwargs = self.resolve_message()
        result = write_file(**kwargs)
        self.send_output(result)
        print(result)
class ContentWriter(AgentBase):
    def execute(self):
        kwargs = self.resolve_message()
        result = content_writer(**kwargs)
        self.send_output(result)
        print(result)
       
class ConversationAgent(AgentBase):

    @add_memory_decorator
    def execute(self):
        kwargs = self.resolve_message()
        kwargs["agent_name"] = self.message.get("to_agent", None)
        kwargs["task_id"] = self.message.get("task_id", "123456")

        response = conversation_agent(**kwargs)

        # Process the response and handle function calls
        choice = response["response"].choices[0]
        message = choice.message

        if message.tool_calls:
            for tool_call in message.tool_calls:
                function_name = tool_call.function.name
                arguments = tool_call.function.arguments

                # Parse the arguments JSON string into a dictionary
                args_dict = json.loads(arguments)

                if function_name == "send_message":
                    # Create the message dictionary
                    message_dict = {
                        "from_agent": response["agent_name"],
                        "to_agent": args_dict.get("agent_name"),
                        "task_id": self.message.get("task_id", "123456"),
                        "message": args_dict.get("query_response"),
                        "args": [
                            {
                                "arg_name": "response",
                                "arg_value": args_dict.get("query_response"),
                                "is_static": True,
                            },
                        ],
                    }

                    self.message_system.send(message_dict)
                   
                    # # Store the result if needed
                    self.data_store[self.message.get("to_agent")] = args_dict.get(
                        "query_response"
                    )

                elif function_name == "stop":
                    print("Convo ended")
                    return "convo ended"

        else:
            print("No function calls in the response.")


