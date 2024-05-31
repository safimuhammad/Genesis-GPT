import logging

def initiate_logging():
    logging.basicConfig(level=logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    for handler_type in [logging.FileHandler, logging.StreamHandler]:
        handler = handler_type('model.log') if handler_type == logging.FileHandler else handler_type()
        handler.setLevel(logging.INFO if handler_type == logging.FileHandler else logging.DEBUG)
        handler.setFormatter(formatter)
        return handler
