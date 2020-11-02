from unittest.mock import MagicMock
import math

import pytest

from Nodes import WaterPurifier


@pytest.mark.parametrize("resources_received, resources_produced", [({"dirty_water": 10}, {"water": 5, "waste": 5}),
                                                                    ({"dirty_water": 10, "oxygen": 10}, {"water": 10, "waste": 10}),
                                                                    ({"dirty_water": 10, "oxygen": 5}, {"water": 7.5, "waste": 7.5}),
                                                                    ({"dirty_water": 7.5, "oxygen": 10}, {"water": 7.5, "waste": 7.5})])
def test_update(resources_received, resources_produced):
    purifier = WaterPurifier.WaterPurifier("omg")

    purifier._resources_received_this_tick = resources_received
    purifier._provideResourceToOutgoingConnections = MagicMock(return_value = 0)
    purifier._getAllReservedResources = MagicMock()

    purifier._temperature = purifier._optimal_temperature

    purifier.update()

    resources_produced_this_tick = purifier.getResourcesProducedThisTick()

    for key in resources_produced:
        assert math.isclose(resources_produced_this_tick[key], resources_produced[key]), "%s doesn't match" % key



