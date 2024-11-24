def add_memory_decorator(func):
    def wrapper(self, *args, **kwargs):
        self.add_memory("input")
        result = func(self, *args, **kwargs)
        self.add_memory("output")
        return result

    return wrapper
