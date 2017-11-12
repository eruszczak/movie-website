def validate_rate(rate):
    """
    rating must be integer 1-10
    """
    try:
        rate = int(rate)
    except (ValueError, TypeError):
        return False
    return 0 < rate < 11
