def serialize_history(history):
    if not history:
        return ""

    return "\n".join([
        item.get("content", "")
        for item in history
    ])