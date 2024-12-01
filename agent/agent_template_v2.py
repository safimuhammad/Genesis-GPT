import logging
from termcolor import colored
from datetime import datetime
from storage.agent_memory import AgentMemory
import uuid         
from datetime import datetime
from .decorators import add_memory_decorator


class AgentBase:
    def __init__(self, logger, message, data_store, message_system):
        self.logger = logger
        self.storage = AgentMemory()
        self.message_system = message_system
        self.data_store = data_store
        self.message = message

    def resolve_message(self):
        try:
            message_args = self.message.get("args", None)
            resolved_args = {}
            if message_args:
                for arg in message_args:
                    is_static = arg.get("is_static", None)
                    if is_static:
                        resolved_args[arg.get("arg_name")] = arg.get("arg_value")
                    else:
                        # data store lookup
                        arg_name = arg.get("arg_name", None)
                        from_agent = self.message.get("from_agent", None)
                        filtered_data_store = self.data_store.get(from_agent, None)
                        if filtered_data_store:
                            resolved_args[arg_name] = filtered_data_store.get(
                                arg_name, None
                            )
            return resolved_args
        except Exception as e:
            self.logger.error(f"Error in resolving message: {e}")

    def report_missing(self, message):
        pass

    def execute(self):
        pass

    def send_output(self, result):
        try:
            if result:
                agent_name = self.message.get("to_agent", None)
                self.data_store[agent_name] = result

        except Exception as e:
            self.logger.error(f"Error in sending output: {e}")

    def add_memory(self, type_):
        try:
            if not self.message:
                raise Exception
            sub_task_id = str(uuid.uuid4())
            timestamp = datetime.now().timestamp()
            # Convert the timestamp to a readable format
            readable_date = datetime.fromtimestamp(timestamp).strftime(
                "%Y-%m-%d %H:%M:%S"
            )

            if type_ == "input":
                self.storage.insert_agent_memory(
                    self.message["task_id"],
                    readable_date,
                    self.message["from_agent"],
                    type_,
                    self.message["message"],
                    None,
                    self.message["to_agent"],
                    sub_task_id,
                    None,
                )
            else:
                result = self.data_store[self.message["to_agent"]]
                self.storage.insert_agent_memory(
                    self.message["task_id"],
                    readable_date,
                    self.message["from_agent"],
                    type_,
                    str(result),
                    None,
                    self.message["to_agent"],
                    sub_task_id,
                    None,
                )

        except Exception as e:
            self.logger.error(f"Error in adding memory: {e}")
