from unittest.mock import MagicMock
import math

import pytest

from Nodes import HydroponicsBay


@pytest.mark.parametrize("resources_received, resources_produced, resources_left_over, effectiveness, oxygen_not_dumped",
                         [({"water": 10}, {"oxygen": 0}, {"water": 10, "energy": 0}, 1, 0),
                          ({"energy": 10}, {"oxygen": 0}, {"energy": 10, "water": 0}, 1, 0),
                          ({"water": 10, "energy": 10}, {"oxygen": 10}, {"water": 0, "energy": 0}, 1, 0),
                          ({"water": 10, "energy": 5}, {"oxygen": 5}, {"water": 5, "energy": 0}, 1, 0),
                          ({"water": 7.5, "energy": 10}, {"oxygen": 7.5}, {"water": 0, "energy": 2.5}, 1, 0),
                          ({"water": 7.5, "energy": 10}, {"oxygen": 3.75}, {"water": 0, "energy": 2.5}, 0.5, 0),
                          ({"water": 7.5, "energy": 10}, {"oxygen": 2.75}, {"water": 2, "energy": 4.5}, 0.5, 1)])  # Since we couldn't dump 1 oxygen (and it doesn't store it), it keeps some water & energy in reserve.
def test_update(resources_received, resources_produced, resources_left_over, effectiveness, oxygen_not_dumped):
    hdydroponics = HydroponicsBay.HydroponicsBay("omg")

    hdydroponics._resources_received_this_tick = resources_received
    hdydroponics._provideResourceToOutgoingConnections = MagicMock(return_value = oxygen_not_dumped)
    hdydroponics._getAllReservedResources = MagicMock()
    hdydroponics._getHealthEffectivenessFactor = MagicMock(return_value=effectiveness)
    hdydroponics._temperature = hdydroponics._optimal_temperature

    hdydroponics.update()

    resources_produced_this_tick = hdydroponics.getResourcesProducedThisTick()

    for key in resources_produced:
        assert math.isclose(resources_produced_this_tick[key], resources_produced[key]), "%s doesn't match" % key

    for key in resources_left_over:
        assert math.isclose(hdydroponics._resources_left_over[key], resources_left_over[key]), "%s doesn't match" % key
