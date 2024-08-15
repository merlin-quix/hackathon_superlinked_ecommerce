import logging


def get_logger():
    # Set up logging
    """
    Initializes a logger named 'waitress' with a level of INFO, and configures it
    to log messages to the console with a specified format. The propagate flag is
    set to False to prevent logging messages from being passed on to higher-level
    handlers.

    Returns:
        loggingLogger: An instance of the Logger class from the Python standard
        library module `logging`. This object represents a single thread's execution
        of the logging module, and it can be used to log messages.

    """
    logger = logging.getLogger('waitress')
    logger.setLevel(logging.INFO)  # Set to DEBUG for more detailed output
    logger.propagate = False  # Prevent the log messages from propagating to the root logger

    # Create handlers (console and file handler for example)
    console_handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger