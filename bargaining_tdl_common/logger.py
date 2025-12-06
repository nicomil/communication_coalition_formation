"""
Structured logging system for bargaining_tdl modules.

Replaces print() statements with proper logging.
"""

import logging
import sys
from typing import Optional

# Configure logger
_logger = logging.getLogger('bargaining_tdl')
_logger.setLevel(logging.INFO)

# Create console handler if not already exists
if not _logger.handlers:
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.INFO)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    handler.setFormatter(formatter)
    
    _logger.addHandler(handler)


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    Get a logger instance for a specific module.
    
    Args:
        name: Optional module name. If None, returns the default logger.
    
    Returns:
        logging.Logger: Logger instance
    """
    if name:
        return logging.getLogger(f'bargaining_tdl.{name}')
    return _logger


# Convenience functions
def info(message: str, *args, **kwargs):
    """Log an info message."""
    _logger.info(message, *args, **kwargs)


def warning(message: str, *args, **kwargs):
    """Log a warning message."""
    _logger.warning(message, *args, **kwargs)


def error(message: str, *args, **kwargs):
    """Log an error message."""
    _logger.error(message, *args, **kwargs)


def debug(message: str, *args, **kwargs):
    """Log a debug message."""
    _logger.debug(message, *args, **kwargs)


# Export default logger as 'logger'
logger = _logger

