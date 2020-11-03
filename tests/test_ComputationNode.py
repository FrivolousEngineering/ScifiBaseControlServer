from unittest.mock import MagicMock
import math

import pytest

from Nodes import ComputationNode


@pytest.mark.parametrize("resources_received, resources_produced", [({"energy": 10}, {"data": 10}),
                                                                    ({"energy": 7.5}, {"data": 7.5})])
def test_update(resources_received, resources_produced):
    computation_node = ComputationNode.ComputationNode("omg")

    computation_node._resources_received_this_tick = resources_received
    computation_node._provideResourceToOutgoingConnections = MagicMock(return_value = 0)
    computation_node._getAllReservedResources = MagicMock()

    computation_node._temperature = computation_node._optimal_temperature

    computation_node.update()

    resources_produced_this_tick = computation_node.getResourcesProducedThisTick()

    for key in resources_produced:
        print(resources_produced_this_tick)
        assert math.isclose(resources_produced_this_tick[key], resources_produced[key]), "%s doesn't match" % key


def test_updateDataNotUsed():
    # Set up two nodes with the only difference being that the one can dump it's data, the other can't
    computation_node_data_used = ComputationNode.ComputationNode("used")
    computation_node_data_used._provideResourceToOutgoingConnections = MagicMock(return_value=0)
    computation_node_data_used._temperature = computation_node_data_used._optimal_temperature
    computation_node_data_used._resources_received_this_tick = {"energy": 10}

    computation_node_data_not_used = ComputationNode.ComputationNode("notUsed")
    computation_node_data_not_used._provideResourceToOutgoingConnections = MagicMock(return_value=10)
    computation_node_data_not_used._temperature = computation_node_data_not_used._optimal_temperature
    computation_node_data_not_used._resources_received_this_tick = {"energy": 10}

    computation_node_data_not_used.update()

    computation_node_data_used.update()

    assert computation_node_data_not_used.temperature < computation_node_data_used.temperature