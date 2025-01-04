import threading
from collections import defaultdict

class Datastore:
    def __init__(self):
        self.store = defaultdict(dict)
        self.lock = threading.Lock()

    def __getitem__(self, key):
        chain_id, agent_name = key
        with self.lock:
            return self.store[chain_id].get(agent_name)

    def __setitem__(self, key, val):
        chain_id, agent_name = key
        with self.lock:
            self.store[chain_id][agent_name] = val

    def get(self, chain_id, agent_name, alt=None):
        with self.lock:
            return self.store[chain_id].get(agent_name, alt)
