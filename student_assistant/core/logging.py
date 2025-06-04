import logging


def get_logger(name: str, log_level=logging.INFO) -> logging.Logger:
    """
    Get a logger with a specific name and configuration.
    Logs only to the console regardless of environment.
    """
    logger = logging.getLogger(name)

    if logger.handlers:
        return logger

    logger.setLevel(log_level)
    
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger