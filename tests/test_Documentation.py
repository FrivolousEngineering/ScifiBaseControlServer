import pytest

from Nodes.Connection import Connection
from Nodes.Node import Node
import inspect
import typing

from Nodes.NodeEngine import NodeEngine

function_exclude_list = ["__new__", "__repr__"]
exclude_signatures = ["kwargs", "args"]


objects_to_check_for_documentation = [Node("whatever"),
                                      NodeEngine(),
                                      Connection(Node("whatever"), Node("whatever2"), "water")]


@pytest.mark.parametrize("object", objects_to_check_for_documentation)
def test_hasDocumentation(object):

    # Make sure that generic documentation exists!
    assert object.__doc__

    for func_name, function in inspect.getmembers(object, predicate = inspect.ismethod):
        if func_name in function_exclude_list:
            continue

        assert function.__doc__, f"Function [{func_name}] of {object.__class__} is not documented"

        sig = inspect.signature(function)

        function_documentation = inspect.getdoc(function)

        for param in sig.parameters:
            if param in exclude_signatures:
                continue

            assert f":param {param}:" in function_documentation, f"Parameter [{param}] of function [{func_name}] of {object.__class__} is not documented"

        try:
            type_hints = typing.get_type_hints(function)
        except NameError:
            # The forward declaration doesn't work quite well for get_type_hints. There is a solution for python 3.7
            # (from __future__ import annotations), but right now this is made for python 3.6
            type_hints = function.__annotations__
        if "return" in type_hints and type_hints["return"] != type(None) and func_name != "__init__":
            assert ":return:" in function_documentation, f"Function function [{func_name}] of {object.__class__} returns something, but this is not documented"


        #assert 0
