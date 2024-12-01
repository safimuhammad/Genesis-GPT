import threading
import time


class MessageDispatcher:
    def __init__(self, message_system, agent_registry, data_store):
        """
        Initializes the MessageDispatcher.

        Args:
            message_system: The messaging system instance used for inter-agent communication.
            agent_registry: A dictionary mapping agent names to their corresponding classes.
            data_store: A shared data store for agent outputs and shared data.
            logger: Logger instance for logging events.
        """
        self.message_system = message_system
        self.agent_registry = agent_registry
        self.data_store = data_store
        self.stop_event = threading.Event()  # Event to signal the dispatcher to stop
        self.dispatcher_thread = None  # Thread will be initialized in start()
        self.logger = ""
        self.cached_agents = {}

    def listen_for_messages(self):
        """
        Continuously listens for incoming messages and dispatches them to the appropriate agents.
        """
        while not self.stop_event.is_set():
            message = self.message_system.receive(timeout=0)
            if message is None:
                continue
            self.dispatch_message(message)

    def start(self):
        """
        Starts the dispatcher in a separate thread.
        """
        self.stop_event.clear()  # Clear the stop event in case it's set
        self.dispatcher_thread = threading.Thread(target=self.listen_for_messages)
        self.dispatcher_thread.start()

    def stop(self):
        """
        Signals the dispatcher to stop listening for messages and waits for the thread to finish.
        """
        self.stop_event.set()
        if self.dispatcher_thread is not None:
            self.dispatcher_thread.join()

    def dispatch_message(self, message):
        to_agent = message["to_agent"]
        if to_agent in self.agent_registry:
            if to_agent in self.cached_agents:
                agent_cls = self.cached_agents[to_agent]
                agent_cls.execute()
            else:
                agent = self.agent_registry[to_agent]
                agent_cls = agent(
                    self.logger, message, self.data_store, self.message_system
                )
                self.cached_agents[to_agent] = agent_cls
                agent_cls.execute()
        else:
            print("Agent not found")
