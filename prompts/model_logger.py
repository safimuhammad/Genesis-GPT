import logging

def initiate_logging():
    logging.basicConfig(level=logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    for handler_type in [logging.FileHandler, logging.StreamHandler]:
        handler = handler_type('prompts/prompt.log') if handler_type == logging.FileHandler else handler_type()
        handler.setLevel(logging.INFO if handler_type == logging.FileHandler else logging.DEBUG)
        handler.setFormatter(formatter)
        return handler

# I know its stupid to keep it here but trust me python relative imports are a mess dont want to slow the progress\n
# down with this stupid stuff
