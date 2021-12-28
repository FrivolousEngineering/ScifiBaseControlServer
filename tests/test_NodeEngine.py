from unittest.mock import MagicMock

from Nodes import NodeEngine
from Nodes.Node import Node
from Nodes.Generator import Generator  # Your IDE lies. It needs this.
from Nodes.FluidCooler import FluidCooler
import pytest

from Nodes.TemperatureHandlers.TemperatureHandler import TemperatureHandler


def createNode(node_id: str):
    return MagicMock(getId = MagicMock(return_value = node_id), spec = Node)


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
    engine._sub_ticks = 1
    node = createNode("test")
    node.requiresReplanning = MagicMock(return_value = False)

    engine.registerNode(node)

    engine.doTick()

    node.preUpdate.assert_called_once()
    node.updateReservations.assert_called_once()
    node.update.assert_called_once()
    node.postUpdate.assert_called_once()

def test_disabledNode():
    engine = NodeEngine.NodeEngine()
    node = createNode("test")
    node.requiresReplanning = MagicMock(return_value=False)
    node.enabled = False

    engine.registerNode(node)

    engine.doTick()

    node.preUpdate.assert_not_called()
    node.updateReservations.assert_not_called()
    node.update.assert_not_called()
    node.postUpdate.assert_not_called()


def test_getAllNodes():
    engine = NodeEngine.NodeEngine()
    node = createNode("test")
    node_2 = createNode("test2")
    engine.registerNode(node)
    engine.registerNode(node_2)

    all_nodes = engine.getAllNodes()
    assert len(all_nodes) == 2
    assert "test" in all_nodes
    assert "test2" in all_nodes
    assert all_nodes["test"] == node
    assert all_nodes["test2"] == node_2


def test_getNodeHistoryById():
    engine = NodeEngine.NodeEngine()
    node = createNode("test")
    engine.registerNode(node)

    assert engine.getNodeHistoryById("test") is not None
    assert engine.getNodeHistoryById("BLARG") is None


# This is a tad more than just a unit test, but it's good to have it since it checks if nodes can be loaded at all
@pytest.mark.parametrize("serialized, all_ids", [({"blarg": {"type": "Node"}}, ["blarg"]),
                                                 ({"omg": {"type": "Generator"}, "zomg": {"type": "Node"}}, ["omg", "zomg"]),
                                                 ({"yay": {"type": "FluidCooler", "resource_type": "water", "fluid_per_tick": 10}}, ["yay"])])
def test_serializeNode(serialized, all_ids):
    engine = NodeEngine.NodeEngine()

    engine._registerNodesFromConfigurationData(serialized)

    assert engine.getAllNodeIds() == all_ids


def test_serializeConnection():
    engine = NodeEngine.NodeEngine()
    node_a = Node("a")
    node_b = Node("b")
    node_a._providable_resources.add("energy")
    node_b._acceptable_resources.add("energy")
    engine.registerNode(node_a)
    engine.registerNode(node_b)

    engine._registerConnectionsFromConfigurationData([{"from": "a", "to": "b", "resource_type": "energy"}])

    node_a_connections = node_a.getAllOutgoingConnectionsByType("energy")
    node_b_connections = node_b.getAllIncomingConnectionsByType("energy")
    assert len(node_a_connections) == 1
    assert len(node_b_connections) == 1

    assert len(node_a.getAllIncomingConnectionsByType("energy")) == 0
    assert len(node_b.getAllOutgoingConnectionsByType("energy")) == 0

    assert node_a_connections[0].target == node_b
    assert node_b_connections[0].origin == node_a


def test_tickCount():
    engine = NodeEngine.NodeEngine()
    assert engine.tick_count == 0

    engine.doTick()
    assert engine.tick_count == 1

    engine.doTick()
    assert engine.tick_count == 2


def test_outsideTemperatureHandler():
    engine = NodeEngine.NodeEngine()

    node = createNode("test")
    node.requiresReplanning = MagicMock(return_value=False) # Prevent engine going into a lock

    engine.registerNode(node)
    temperature_handler = MagicMock(spec = TemperatureHandler)
    temperature_handler.getTemperatureForTick = MagicMock(return_value = 200)
    engine.setOutsideTemperatureHandler(temperature_handler)

    engine.doTick()

    assert node.outside_temp == 200

