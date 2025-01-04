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
        self.chain_id = message.get("chain_id")

        if not self.chain_id:
            self.logger.error("No 'chain_id' found in the message.")
            raise ValueError("Agent must have a 'chain_id' to function correctly.")

    def resolve_message(self):
        try:
            message_args = self.message.get("args", None)
            resolved_args = {}
            if message_args:
                for arg in message_args:
                    is_static = arg.get("is_static", None)
                    arg_name = arg.get("arg_name")
                    if not arg_name:
                        self.logger.warning(
                            "Argument without 'arg_name' found; skipping."
                        )
                        continue
                    if is_static:
                        resolved_args[arg_name] = arg.get("arg_value")
                    else:
                        # data store lookup
                        from_agent = self.message.get("from_agent", None)
                        if not from_agent:
                            self.logger.warning(
                                f"No 'from_agent' specified for dynamic argument '{arg_name}'; skipping."
                            )
                            continue
                        datastore_key = (self.chain_id, from_agent)
                        filtered_data_store = self.data_store.get(
                            self.chain_id, from_agent
                        )
                        if filtered_data_store and arg_name in filtered_data_store:
                            resolved_args[arg_name] = filtered_data_store[arg_name]
                        else:
                            self.logger.warning(
                                f"No data found for key {datastore_key} and argument '{arg_name}'."
                            )
            return resolved_args
        except Exception as e:
            self.logger.error(f"Error in resolving message: {e}")
            return {}

    def report_missing(self, message):
        pass

    def execute(self):
        pass

    def send_output(self, result):
        try:
            if result:
                agent_name = self.message.get("to_agent", None)
                if not agent_name:
                    raise Exception("No agent specified in the message")
                self.data_store[self.chain_id, agent_name] = result

                self.logger.info(
                    f"Output from agent '{agent_name}' stored in datastore with chain_id {self.chain_id}."
                )
        except Exception as e:
            self.logger.error(f"Error in sending output: {e}")

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
            from_agent = self.message.get("from_agent")
            to_agent = self.message.get("to_agent")
            task_id = self.message.get("task_id")

            if not from_agent or not to_agent or not task_id:
                raise ValueError(
                    "Message is missing required fields ('from_agent', 'to_agent', 'task_id')."
                )

            if type_ == "input":
                # Log input data
                self.storage.insert_agent_memory(
                    from_agent=from_agent,
                    task_id=task_id,
                    timestamp=readable_date,
                    type_=type_,
                    message=self.message.get("message"),
                    additional_info=None,
                    to_agent=to_agent,
                    sub_task_id=sub_task_id,
                    extra=None,
                )
            else:
                datastore_key = (self.chain_id, to_agent)
                result = self.data_store.get(self.chain_id, to_agent)
                if result is None:
                    raise ValueError(
                        f"No result found in datastore for key {datastore_key}."
                    )

                # Log output data
                self.storage.insert_agent_memory(
                    task_id=task_id,
                    timestamp=readable_date,
                    from_agent=from_agent,
                    type_=type_,
                    message=str(result),
                    additional_info=None,
                    to_agent=to_agent,
                    sub_task_id=sub_task_id,
                    extra=None,
                )
            self.logger.info(
                f"Memory added for agent '{to_agent}' with type '{type_}' and key '{datastore_key}'."
            )

        except Exception as e:
            self.logger.error(f"Error in adding memory: {e}")
