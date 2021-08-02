import pytest

from Nodes.Node import Node
import inspect

function_exclude_list = ["__new__", "__repr__"]
exclude_signatures = ["kwargs", "args"]


objects_to_check_for_documentation = [Node("whatever")]


@pytest.mark.parametrize("object", objects_to_check_for_documentation)
def test_hasDocumentation(object):

    # Make sure that generic documentation exists!
    assert object.__doc__

    for func_name, function in inspect.getmembers(object, predicate = inspect.ismethod):
        if func_name in function_exclude_list:
            continue

        assert function.__doc__, f"Function [{func_name}] of {object.__class__} is not documented"

        sig = inspect.signature(function)
        for param in sig.parameters:
            if param in exclude_signatures:
                continue

            assert f":param {param}:" in inspect.getdoc(function), f"Parameter [{param}] of function [{func_name}] of {object.__class__} is not documented"