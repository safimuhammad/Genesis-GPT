import queue


class InMemoryMessageSystem:
    def __init__(self):
        self.queue = queue.Queue()

    def send(self, message):
        self.queue.put(message)

    def receive(self, timeout=0):
        try:
            message = self.queue.get(timeout=timeout)
            return message
        except queue.Empty:
            return None
