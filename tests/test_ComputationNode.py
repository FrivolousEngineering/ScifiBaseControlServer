from unittest.mock import MagicMock
import math

import pytest

from Nodes import ComputationNode


@pytest.mark.parametrize("resources_received, resources_produced", [({"energy": 10}, {"data": 10}),
                                                                    ({"energy": 7.5}, {"data": 7.5}),
                                                                    ({"energy": 0}, {"data": 0})])
def test_update(resources_received, resources_produced):
    computation_node = ComputationNode.ComputationNode("omg")

    computation_node._resources_received_this_sub_tick = resources_received
    computation_node._provideResourceToOutgoingConnections = MagicMock(return_value = 0)
    computation_node._getAllReservedResources = MagicMock()

    computation_node._temperature = computation_node._optimal_temperature

    computation_node.update()

    resources_produced_this_tick = computation_node.getResourcesProducedThisTick()

    for key in resources_produced:
        assert math.isclose(resources_produced_this_tick[key], resources_produced[key]), "%s doesn't match" % key


def test_updateDataNotUsed():
    # Set up two nodes with the only difference being that the one can dump it's data, the other can't
    computation_node_data_used = ComputationNode.ComputationNode("used")
    computation_node_data_used._provideResourceToOutgoingConnections = MagicMock(return_value=0)
    computation_node_data_used._temperature = computation_node_data_used._optimal_temperature
    computation_node_data_used._resources_received_this_sub_tick = {"energy": 10}

    computation_node_data_not_used = ComputationNode.ComputationNode("notUsed")
    computation_node_data_not_used._provideResourceToOutgoingConnections = MagicMock(return_value=10)
    computation_node_data_not_used._temperature = computation_node_data_not_used._optimal_temperature
    computation_node_data_not_used._resources_received_this_sub_tick = {"energy": 10}
    computation_node_data_not_used.update()
    computation_node_data_used.update()

    assert computation_node_data_not_used.temperature < computation_node_data_used.temperature

def test_couldntStoreALlData():
    computation_node = ComputationNode.ComputationNode("omg")
    computation_node._resources_received_this_sub_tick = {"energy": 10}
    computation_node._getAllReservedResources = MagicMock()
    computation_node._temperature = computation_node._optimal_temperature
    computation_node._provideResourceToOutgoingConnections = MagicMock(return_value=1)
    computation_node.update()

    # Even though the node got the power to produce 10, it couldn't actually do so.
    # Since data is a use it or lose it, it didn't actually generate the data.
    assert math.isclose(computation_node.getResourcesProducedThisTick()["data"], 9)


def test_effectivenessFactor():
    computation_node = ComputationNode.ComputationNode("omg")
    computation_node._resources_received_this_sub_tick = {"energy": 10}
    computation_node._getAllReservedResources = MagicMock()
    computation_node._temperature = computation_node._optimal_temperature
    computation_node._provideResourceToOutgoingConnections = MagicMock(return_value=0)
    computation_node._getHealthEffectivenessFactor = MagicMock(return_value = 0.25)

    computation_node.update()

    assert math.isclose(computation_node.getResourcesProducedThisTick()["data"], 2.5)

    computation_node._provideResourceToOutgoingConnections.assert_called_with("data", 2.5)