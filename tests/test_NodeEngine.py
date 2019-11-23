from unittest.mock import MagicMock

from Nodes import NodeEngine
from Nodes.Node import Node
import pytest


def createNode(node_id: str):
    return MagicMock(getId = MagicMock(return_value = node_id), Spec = Node)


def test_registerNode():
    engine = NodeEngine.NodeEngine()
    engine.registerNode(createNode("ZOMG"))

    assert engine.getAllNodeIds() == ["ZOMG"]


def test_registerDuplicateId():
    engine = NodeEngine.NodeEngine()
    engine.registerNode(createNode("ZOMG"))
    with pytest.raises(KeyError):
        engine.registerNode(createNode("ZOMG"))


def test_replanReservations():
    engine = NodeEngine.NodeEngine()

    node = createNode("test")
    node.requiresReplanning = MagicMock(side_effect = [True, True, False])
    engine.registerNode(node)

    engine._replanReservations()

    assert node.replanReservations.call_count == 2


def test_doTick():
    engine = NodeEngine.NodeEngine()
    node = createNode("test")
    node.requiresReplanning = MagicMock(return_value = False)

    engine.registerNode(node)

    engine.doTick()

    node.preUpdate.assert_called_once()
    node.updateReservations.assert_called_once()
    node.update.assert_called_once()
    node.postUpdate.assert_called_once()
