from memory.datastore import Datastore
from memory.message_system import InMemoryMessageSystem
from memory.message_dispatcher import MessageDispatcher
import threading
import time
from agent.agents import ReadAgent, WriteAgent, ConversationAgent
import signal
import uuid


def signal_handler(sig, frame):
    print("Signal received. Stopping dispatcher...")
    dispatcher.stop()
    print("Dispatcher stopped gracefully.")
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)
data_store = Datastore()
data_store["read_file"] = {"data": "read data store values"}
data_store["write_file"] = {"data": "write data store values"}
message_system = InMemoryMessageSystem()
agent_registy = {
    "read_file": ReadAgent,
    "write_file": WriteAgent,
    "bob": ConversationAgent,
    "alice": ConversationAgent,
    "kevin": ConversationAgent,
    "safi": ConversationAgent,
}
dispatcher = MessageDispatcher(message_system, agent_registy, data_store)
dispatcher.start()


message = {
    "from_agent": "kevin",
    "to_agent": "bob",
    "task_id": str(uuid.uuid4()),
    "message": "initiate conversation",
    "args": [
        {
            "arg_name": "response",
            "arg_value": "lets talk!",
            "is_static": True,
        },
    ],
}

message_system.send(message)


time.sleep(30)
dispatcher.stop()
