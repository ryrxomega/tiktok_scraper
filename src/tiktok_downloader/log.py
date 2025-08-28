"""
This module provides logging configuration for the application.

It sets up a standard logger that can be configured with different
verbosity levels.
"""
import logging
import sys

def setup_logging(verbosity: int = 0):
    """
    Configures the root logger for the application.

    Args:
        verbosity: The desired verbosity level.
                   0 for WARNING, 1 for INFO, 2 or more for DEBUG.
    """
    log_level = logging.WARNING
    if verbosity == 1:
        log_level = logging.INFO
    elif verbosity >= 2:
        log_level = logging.DEBUG

    # Create a handler that writes to stderr
    handler = logging.StreamHandler(sys.stderr)
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)

    # Get the root logger and configure it
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Avoid adding handlers multiple times
    if not root_logger.handlers:
        root_logger.addHandler(handler)
