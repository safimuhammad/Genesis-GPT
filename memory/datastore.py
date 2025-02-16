
import threading
from collections import defaultdict
import json

class Datastore:
    def __init__(self, redis_config=None):
        """
        Initializes the datastore. If redis_config is provided, the datastore
        uses Redis as backend; otherwise, it falls back to an in-memory store.
        """
        self.redis = None
        if redis_config:
            try:
                import redis
                self.redis = redis.Redis(**redis_config)
            except ImportError:
                raise ImportError("redis module not installed, but redis_config provided.")
        if not self.redis:
            self.store = defaultdict(dict)
            self.locks = defaultdict(threading.Lock)

    def _get_lock(self, chain_id):
        if self.redis:
            return None
        return self.locks[chain_id]

    def __getitem__(self, key):
        """
        Retrieve a value using the key tuple (chain_id, agent_name).
        """
        chain_id, agent_name = key
        if self.redis:
            key_str = f"{chain_id}:{agent_name}"
            value = self.redis.get(key_str)
            return json.loads(value) if value is not None else None
        else:
            lock = self._get_lock(chain_id)
            with lock:
                return self.store[chain_id].get(agent_name)

    def __setitem__(self, key, val):
        """
        Store a value using the key tuple (chain_id, agent_name).
        """
        chain_id, agent_name = key
        if self.redis:
            key_str = f"{chain_id}:{agent_name}"
            # Convert the value to JSON before storing
            self.redis.set(key_str, json.dumps(val))
        else:
            lock = self._get_lock(chain_id)
            with lock:
                self.store[chain_id][agent_name] = val

    def get(self, chain_id, agent_name, alt=None):
        """
        Retrieve a value given a chain_id and agent_name.
        If not found, returns the alternative value provided in alt.
        """
        if self.redis:
            key_str = f"{chain_id}:{agent_name}"
            value = self.redis.get(key_str)
            return json.loads(value) if value is not None else alt
        else:
            lock = self._get_lock(chain_id)
            with lock:
                return self.store[chain_id].get(agent_name, alt)