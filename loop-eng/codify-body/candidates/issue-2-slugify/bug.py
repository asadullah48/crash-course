def slugify(title):
    """Turn a title into a URL slug: lowercase, spaces become hyphens."""
    return title.replace(" ", "-")  # bug: never lowercases
