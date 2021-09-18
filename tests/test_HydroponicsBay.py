from unittest.mock import MagicMock
import math

import pytest

from Nodes import HydroponicsBay
from tests.testHelpers import createEngineFromConfig


@pytest.mark.parametrize("resources_received, resources_provided, resources_left_over, effectiveness, oxygen_not_dumped",
                         [({"water": 10}, {"oxygen": 0}, {"water": 0, "energy": 0}, 1, 0),
                          ({"energy": 10}, {"oxygen": 0}, {"energy": 10, "water": 0}, 1, 0),
                          ({"water": 10, "energy": 10}, {"oxygen": 10}, {"water": 0, "energy": 0}, 1, 0),
                          ({"water": 10, "energy": 5}, {"oxygen": 5}, {"water": 0, "energy": 0}, 1, 0),
                          ({"water": 7.5, "energy": 10}, {"oxygen": 7.5}, {"water": 0, "energy": 2.5}, 1, 0),
                          ({"water": 7.5, "energy": 10}, {"oxygen": 3.75}, {"water": 0, "energy": 2.5}, 0.5, 0),
                          ({"water": 7.5, "energy": 10}, {"oxygen": 2.75}, {"water": 1, "energy": 4.5}, 0.5, 1)])  # Since we couldn't dump 1 oxygen (and it doesn't store it), it keeps some water & energy in reserve.
def test_update(resources_received, resources_provided, resources_left_over, effectiveness, oxygen_not_dumped):
    hydroponics = HydroponicsBay.HydroponicsBay("omg")

    hydroponics._resources_received_this_sub_tick = resources_received
    hydroponics._provideResourceToOutgoingConnections = MagicMock(return_value = oxygen_not_dumped)
    hydroponics._getAllReservedResources = MagicMock()
    hydroponics._getHealthEffectivenessFactor = MagicMock(return_value=effectiveness)
    hydroponics._temperature = hydroponics._optimal_temperature
    hydroponics.ensureSaneValues()
    hydroponics.update()

    resources_provided_this_tick = hydroponics.getResourcesProvidedThisTick()

    for key in resources_provided:
        assert math.isclose(resources_provided_this_tick[key], resources_provided[key]), "%s doesn't match %s: %s" % (key, resources_provided_this_tick[key], resources_provided[key])

    for key in resources_left_over:
        assert math.isclose(hydroponics._resources_left_over[key], resources_left_over[key]), "%s doesn't match %s: %s" % (key, hydroponics._resources_left_over[key], resources_left_over[key])


def test_temperatureRemainTheSame():
    # Not quite a unit test; But create a simple setup.
    # Since the hydroponics does not create energy, it should just stay the same temperature
    engine = createEngineFromConfig("HydroponicsSetup.json")
    hydroponics = engine.getNodeById("hydroponics")
    temperature_before = hydroponics.temperature
    engine.doTick()
    engine.doTick()

    assert math.isclose(temperature_before, hydroponics.temperature)


def test_temperatureRemainTheSameOptimalTemperature():
    # Not quite a unit test; But create a simple setup.
    # Since the hydroponics does not create energy, it should just stay the same temperature.
    # For this test, we set the temp of all nodes at the perfect hydroponics temp (so that it actually creates resources!)
    engine = createEngineFromConfig("HydroponicsSetup.json")
    engine._sub_ticks = 1

    hydroponics = engine.getNodeById("hydroponics")
    engine._default_outside_temperature = hydroponics._optimal_temperature
    # Ensure that all nodes are at the perfect temperature
    for node in engine.getAllNodes().values():
        node._temperature = hydroponics._optimal_temperature
        node.outside_temp = hydroponics._optimal_temperature
        node.ensureSaneValues()

    temperature_before = hydroponics.temperature
    for _ in range(0, 10):
        engine.doTick()
        assert math.isclose(temperature_before, hydroponics.temperature)

