from unittest.mock import MagicMock

from Nodes import NodeEngine
import pytest


def createNode(node_id: str):
    return MagicMock(getId = MagicMock(return_value = node_id))


def test_registerNode():
    engine = NodeEngine.NodeEngine()
    engine.registerNode(createNode("ZOMG"))

    assert engine.getAllNodeIds() == ["ZOMG"]


def test_registerDuplicateId():
    engine = NodeEngine.NodeEngine()
    engine.registerNode(createNode("ZOMG"))
    with pytest.raises(KeyError):
        engine.registerNode(createNode("ZOMG"))


