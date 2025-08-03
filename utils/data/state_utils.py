"""Utility functions for state abbreviation handling"""

def normalize_state_abbreviation(state_str):
    """
    Normalize state abbreviation to uppercase, with proper handling
    
    Args:
        state_str: The state abbreviation string
        
    Returns:
        Properly formatted state abbreviation (uppercase)
    """
    if not state_str:
        return ""
    
    # Strip any whitespace and convert to uppercase
    return state_str.strip().upper()
