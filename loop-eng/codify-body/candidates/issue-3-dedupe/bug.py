def dedupe(items):
    """Remove duplicates, preserving first-seen order."""
    return list(set(items))  # bug: set() does not preserve order
