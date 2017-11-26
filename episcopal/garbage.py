from episcopal.runtime import RuntimeObject


def get_children(obj: RuntimeObject):
    return obj.children()
