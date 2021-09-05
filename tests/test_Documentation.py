import pytest

from Nodes.Connection import Connection
from Nodes.Generator import Generator
from Nodes.Node import Node
import inspect
import typing

from Nodes.NodeEngine import NodeEngine
from Nodes.NodeHistory import NodeHistory

function_exclude_list = ["__new__", "__repr__"]
exclude_signatures = ["kwargs", "args"]


objects_to_check_for_documentation = [Node("whatever"),
                                      NodeEngine(),
                                      Connection(Node("whatever"), Node("whatever2"), "water"),
                                      NodeHistory(Node("NodeHistory")),
                                      Generator("generator")]

# In order to get a single test per function, we generate the list here so we can use parametrize later to make sure
# that multiple functions that are missing documentation will result in multiple failed tests.
# If we don't do this, the tests will stop checking if a single function isn't documented.
functions_to_check_for_documentation = []
for obj in objects_to_check_for_documentation:
    for func_name, function in inspect.getmembers(obj, predicate = inspect.ismethod):
        if func_name not in function_exclude_list:
            functions_to_check_for_documentation.append((obj.__class__, func_name, function))


@pytest.mark.parametrize("object", objects_to_check_for_documentation)
def test_objectHasDocumentation(object):
    # Make sure that generic documentation exists.
    # Also note that this is an *explicit* check for the __doc__ and not the inspect.getdoc. This is on purpose; sub
    # classes should at least have a base documentation that isn't inherited from its parent class.
    assert object.__doc__


@pytest.mark.parametrize("class_name, func_name, function", functions_to_check_for_documentation)
def test_functionHasDocumentation(class_name, func_name, function):
    function_documentation = inspect.getdoc(function)
    assert function_documentation, f"Function [{func_name}] of {class_name} is not documented at all"

    sig = inspect.signature(function)

    for param in sig.parameters:
        if param in exclude_signatures:
            continue

        assert f":param {param}:" in function_documentation, f"Parameter [{param}] of function [{func_name}] of {class_name} is not documented"

    try:
        type_hints = typing.get_type_hints(function)
    except NameError:
        # The forward declaration doesn't work quite well for get_type_hints. There is a solution for python 3.7
        # (from __future__ import annotations), but right now this is made for python 3.6
        type_hints = function.__annotations__
    if "return" in type_hints and type_hints["return"] != type(None) and func_name != "__init__":
        assert ":return:" in function_documentation, f"Function function [{func_name}] of {object.__class__} returns something, but this is not documented"