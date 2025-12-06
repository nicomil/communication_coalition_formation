"""
Helper functions shared across bargaining_tdl modules.
"""


def save_time_value(time_value, default=0.0):
    """
    Helper function to safely convert time_on_page value to float.
    
    Args:
        time_value: The time value to convert (can be None, empty string, or numeric)
        default: Default value to return if conversion fails (default: 0.0)
    
    Returns:
        float: The converted time value, or default if conversion fails
    """
    if time_value is None or time_value == '':
        return default
    try:
        return float(time_value)
    except (ValueError, TypeError):
        return default

