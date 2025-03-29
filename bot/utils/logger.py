import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def get_logger(name):
    """
    Returns a logger with the specified name.
    """
    return logging.getLogger(name)
