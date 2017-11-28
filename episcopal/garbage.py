from episcopal.runtime import RuntimeObject


def get_children(obj: RuntimeObject):
    """
    Returns all children of the specified cell value.
    """
    return obj.children()
