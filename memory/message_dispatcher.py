import threading
import logging
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
import queue
class MessageDispatcher:
    def __init__(self, message_system, agent_registry, data_store,max_workers=5):
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
        self.logger = logging.getLogger("MessageDispatcher")
        self.cached_agents = {}
        self.chain_queues = defaultdict(queue.Queue)  # Separate queue per chain_id
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.active_chains = set()

    def listen_for_messages(self):
        """
        Continuously listens for incoming messages and dispatches them to the appropriate agents.
        """
        while not self.stop_event.is_set():
            message = self.message_system.receive(timeout=5)
            if message:
                chain_id = message.get("chain_id", None)
                if chain_id:
                    self.chain_queues[chain_id].put(message)
                    if chain_id not in self.active_chains:
                        self.active_chains.add(chain_id)
                        self.executor.submit(self.dispatch_chain, chain_id)
                else:
                    self.logger.error("Received message without chain_id")
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
        if self.dispatcher_thread:
            self.dispatcher_thread.join()
        self.executor.shutdown(wait=True)   

    def dispatch_chain(self, chain_id):
        """
        Dispatches messages from a specific chain.
        """
        q = self.chain_queues[chain_id]
        while not q.empty() and not self.stop_event.is_set():
            message = q.get()
            self.dispatch_message(message)
            q.task_done()
        self.active_chains.remove(chain_id)
        if not q.empty() and not self.stop_event.is_set():
            if chain_id not in self.active_chains:
                self.active_chains.add(chain_id)
                self.executor.submit(self.dispatch_chain, chain_id)
        else:
            del self.chain_queues[chain_id]

    def dispatch_message(self, message):
        to_agent = message["to_agent"]
        chain_id = message["chain_id"]
        if to_agent in self.agent_registry:
            agent_key = (chain_id, to_agent)
            if agent_key in self.cached_agents:
                agent_cls = self.cached_agents[agent_key]
                agent_cls.execute()
            else:
                agent = self.agent_registry[to_agent]
                agent_cls = agent(
                    self.logger, message, self.data_store, self.message_system
                )
                self.cached_agents[agent_key] = agent_cls
                agent_cls.execute()
        else:
            self.logger.error(f"Agent '{to_agent}' not found for chain '{chain_id}'")
