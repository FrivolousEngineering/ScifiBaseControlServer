from unittest.mock import MagicMock

import Node
import pytest

def test_getId():
    node = Node.Node("zomg")
    assert node.getId() == "zomg"


def test_addHeat():
    node = Node.Node("yay")

    starting_temp = node.temperature
    node.addHeat(300)
    assert node.temperature == starting_temp + 1


def test_connect():
    node_1 = Node.Node("zomg")
    node_2 = Node.Node("omg")

    node_1.connectWith("energy", node_2)

    assert len(node_1.getAllOutgoingConnectionsByType("energy")) == 1
    assert len(node_2.getAllIncomingConnectionsByType("energy")) == 1


@pytest.mark.parametrize("starting_temperature, outside_temperature, heat_emitted", [(0, 0, 0),
                                                                                     (200, 200, 0),
                                                                                     (201, 200, -0.91402670835),
                                                                                     (200, 201, 0.91402670835),
                                                                                     (200, 202, 1.8417978936)])
def test__emitHeat(starting_temperature, outside_temperature, heat_emitted):
    node = Node.Node("")
    node.addHeat = MagicMock()
    node.outside_temp = outside_temperature

    # Force the starting temperature
    node._temperature = starting_temperature

    node._emitHeat()

    node.addHeat.assert_called_with(heat_emitted)


@pytest.mark.parametrize("starting_temperature, outside_temperature, heat_emitted", [(0, 0, 0),
                                                                                     (200, 200, 0),
                                                                                     (201, 200, -10),
                                                                                     (200, 201, 10),
                                                                                     (200, 202, 20)])
def test__convectiveHeatTransfer(starting_temperature, outside_temperature, heat_emitted):
    node = Node.Node("")
    node.addHeat = MagicMock()
    node.outside_temp = outside_temperature
    # Force the starting temperature
    node._temperature = starting_temperature

    node._convectiveHeatTransfer()
    node.addHeat.assert_called_with(heat_emitted)


def test__requiresReplanningNoConnections():
    node = Node.Node("")
    assert not node.requiresReplanning()