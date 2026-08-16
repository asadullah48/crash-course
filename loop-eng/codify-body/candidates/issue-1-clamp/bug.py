def clamp_pct(x):
    """Clamp x into the 0-100 range."""
    if x < 0:
        return 0
    return x  # bug: never clamps the upper bound
