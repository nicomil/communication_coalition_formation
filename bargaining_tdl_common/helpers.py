"""
Helper functions shared across bargaining_tdl modules.
"""

from .logger import get_logger

logger = get_logger('helpers')


def save_time_value(time_value, default=0.0):
    """
    Helper function to safely convert time_on_page value to float.
    
    This function handles various input types and edge cases, ensuring that
    time tracking values are always valid floats. Used extensively throughout
    the application for time tracking on pages.
    
    Args:
        time_value: The time value to convert. Can be:
            - None
            - Empty string ('')
            - Numeric string (e.g., '10.5')
            - Float or int
        default: Default value to return if conversion fails (default: 0.0)
    
    Returns:
        float: The converted time value, or default if conversion fails
    
    Example:
        >>> save_time_value('10.5')
        10.5
        >>> save_time_value(None)
        0.0
        >>> save_time_value('invalid', default=5.0)
        5.0
    """
    if time_value is None or time_value == '':
        return default
    try:
        result = float(time_value)
        # Valida che il risultato sia ragionevole (non negativo, non infinito)
        if result < 0:
            logger.warning(f"Negative time value: {time_value}, using default {default}")
            return default
        if not (0 <= result < 1e6):  # Max 1 milione di secondi (~11 giorni)
            logger.warning(f"Unreasonable time value: {time_value}, using default {default}")
            return default
        return result
    except (ValueError, TypeError) as e:
        logger.debug(f"Could not convert time value '{time_value}': {e}, using default {default}")
        return default

