import sys
from typing import Any

def strToClass(class_name: str) -> Any:
    """
    Get a a class in the Nodes module by providing a string that identifies it
    :param class_name:
    :return:
    """
    module = getattr(sys.modules[__name__], class_name)
    # Since we ensure that the module always has the same name as the class, this will work
    result_class = getattr(module, class_name)
    return result_class
