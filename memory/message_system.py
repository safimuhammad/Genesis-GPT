# message_system.py
import queue
import logging

class InMemoryMessageSystem:
    def __init__(self):
        self.queue = queue.Queue()
        self.logger = logging.getLogger("InMemoryMessageSystem")

    def send(self, message):
        self.logger.debug(f"Sending message: {message}")
        self.queue.put(message)

    def receive(self, timeout=0):
        try:
            message = self.queue.get(timeout=timeout)
            return message
        except queue.Empty:
            return None