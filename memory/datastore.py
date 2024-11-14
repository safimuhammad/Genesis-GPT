import threading


class Datastore:
    def __init__(self):
        self.store = {}
        self.lock = threading.Lock()

    def __getitem__(self, key):
        with self.lock:
            return self.store.get(key)

    def __setitem__(self, key, val):
        with self.lock:
            self.store[key] = val

    def get(self, key, alt):
        with self.lock:
            return self.store.get(key, alt)
