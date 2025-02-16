# message_dispatcher.py
import threading
import logging
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
import queue

class MessageDispatcher:
    def __init__(self, message_system, agent_registry, data_store, max_workers=5):
        self.message_system = message_system
        self.agent_registry = agent_registry
        self.data_store = data_store
        self.stop_event = threading.Event()
        self.dispatcher_thread = None
        self.logger = logging.getLogger("MessageDispatcher")
        self.cached_agents = {}
        self.chain_queues = defaultdict(queue.Queue)
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.active_chains = set()

        # New locks for thread safety
        self._active_chains_lock = threading.Lock()
        self._cached_agents_lock = threading.Lock()
        self._chain_queues_lock = threading.Lock()


    def listen_for_messages(self):
        while not self.stop_event.is_set():
            try:
                message = self.message_system.receive(timeout=5)
                if message:
                    chain_id = message.get("chain_id")
                    if chain_id:
                        self.chain_queues[chain_id].put(message)
                        if chain_id not in self.active_chains:
                            self.active_chains.add(chain_id)
                            self.executor.submit(self.dispatch_chain, chain_id)
                    else:
                        self.logger.error("Received message without chain_id")
            except Exception as e:
                self.logger.error(f"Error in listen_for_messages: {e}")

    def start(self):
        self.stop_event.clear()
        self.dispatcher_thread = threading.Thread(target=self.listen_for_messages, daemon=True)
        self.dispatcher_thread.start()

    def stop(self):
        self.stop_event.set()
        if self.dispatcher_thread:
            self.dispatcher_thread.join()
        self.executor.shutdown(wait=True)

    def dispatch_chain(self, chain_id):
        q = self.chain_queues.get(chain_id)
        while q and not self.stop_event.is_set():
            try:
                # Use blocking get with timeout to reduce busy waiting
                message = q.get(timeout=1)
                self.dispatch_message(message)
                q.task_done()
            except queue.Empty:
                break
            except Exception as e:
                self.logger.error(f"Error dispatching message for chain {chain_id}: {e}")
        self.active_chains.discard(chain_id)
        # If new messages arrived during processing, reschedule the chain
        if q and not q.empty() and not self.stop_event.is_set():
            if chain_id not in self.active_chains:
                self.active_chains.add(chain_id)
                self.executor.submit(self.dispatch_chain, chain_id)
        else:
            self.chain_queues.pop(chain_id, None)

    def dispatch_message(self, message):
        try:
            to_agent = message["to_agent"]
            chain_id = message["chain_id"]
            if to_agent in self.agent_registry:
                agent_key = (chain_id, to_agent)
                if agent_key in self.cached_agents:
                    agent_instance = self.cached_agents[agent_key]
                    agent_instance.execute()
                else:
                    agent_class = self.agent_registry[to_agent]
                    agent_instance = agent_class(
                        self.logger, message, self.data_store, self.message_system
                    )
                    self.cached_agents[agent_key] = agent_instance
                    agent_instance.execute()
            else:
                self.logger.error(f"Agent '{to_agent}' not found for chain '{chain_id}'")
        except Exception as e:
            self.logger.error(f"Error dispatching message: {e}")