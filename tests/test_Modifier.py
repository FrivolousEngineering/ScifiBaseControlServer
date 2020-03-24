from unittest.mock import MagicMock

import pytest

from Nodes.Modifiers import Modifier
from Nodes import Node


@pytest.mark.parametrize("mod_1, mod_2, result", [(Modifier.Modifier(), None, False),
                                                  (Modifier.Modifier(), Modifier.Modifier(duration = 12), False),
                                                  (Modifier.Modifier(modifiers = {"omg": 12}), Modifier.Modifier(), False),
                                                  (Modifier.Modifier(factors = {"omg": 12}), Modifier.Modifier(), False)])
def test_compare(mod_1, mod_2, result):
    assert (mod_1 == mod_2) == result


def test_name():
    assert Modifier.Modifier().name == "Modifier"

def test_getSetNode():
    mod = Modifier.Modifier()
    mock_node = MagicMock(spec = Node.Node)
    mod.setNode(mock_node)
    assert mod.getNode() == mock_node