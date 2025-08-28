"""
Configures the logging for the application.
"""
import logging
import sys

def setup_logging(level: int = logging.INFO):
    """
    Sets up a console logger for the application.

    Args:
        level: The logging level to use (e.g., logging.INFO, logging.DEBUG).
    """
    # Get the root logger
    logger = logging.getLogger()
    logger.setLevel(level)

    # Create a handler to write to standard error
    handler = logging.StreamHandler(sys.stderr)
    handler.setLevel(level)

    # Create a formatter and add it to the handler
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)

    # Add the handler to the logger
    # Clear existing handlers to avoid duplicate logs in testing environments
    if logger.hasHandlers():
        logger.handlers.clear()
    logger.addHandler(handler)
