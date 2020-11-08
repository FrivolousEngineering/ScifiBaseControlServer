from unittest.mock import MagicMock
import math

import pytest

from Nodes import WaterPurifier


@pytest.mark.parametrize("resources_received,                   resources_produced",
                        [({"dirty_water": 10},                  {"water": 5, "waste": 5}),
                         ({"dirty_water": 10, "oxygen": 10},    {"water": 10, "waste": 10}),
                         ({"dirty_water": 10, "oxygen": 5},     {"water": 7.5, "waste": 7.5}),
                         ({"dirty_water": 7.5, "oxygen": 10},   {"water": 7.5, "waste": 7.5}),
                         ({"oxygen": 10},                       {"water": 0, "waste": 0})])
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

    # Ensure that the an attempt was made to provide energy (20!)
    assert purifier._provideResourceToOutgoingConnections.call_args_list[0][0][0] == "water"
    assert math.isclose(purifier._provideResourceToOutgoingConnections.call_args_list[0][0][1], resources_produced["water"])

    # Ensure that an attempt was made to provide water (0!)
    assert purifier._provideResourceToOutgoingConnections.call_args_list[1][0][0] == "waste"
    assert math.isclose(purifier._provideResourceToOutgoingConnections.call_args_list[1][0][1], resources_produced["waste"])



@pytest.mark.parametrize("waste_left,   water_left, oxygen_required,    dirty_water_required,   health_effectiveness_factor",
                         [(1,           9,          1,                  1,                      1),
                          (9,           1,          1,                  1,                      1),
                          (0,           0,          10,                 10,                     1),
                          (0,           0,          5,                  5,                      0.5),
                          (3,           3,          2,                  2,                      0.5),
                          (8,           2,          0,                  0,                      0.5),  # More left than needed!
                          (1,           1,          1,                  1,                      0.2)
                                                                                              ])
def test__update_resources_required_per_tick(waste_left, water_left, oxygen_required, dirty_water_required, health_effectiveness_factor):
    water_purifier = WaterPurifier.WaterPurifier("omg")
    water_purifier._resources_left_over["waste"] = waste_left
    water_purifier._resources_left_over["water"] = water_left
    water_purifier._getHealthEffectivenessFactor = MagicMock(return_value = health_effectiveness_factor)
    water_purifier._updateResourceRequiredPerTick()

    assert math.isclose(water_purifier._resources_required_per_tick["dirty_water"], dirty_water_required)
    assert math.isclose(water_purifier._resources_required_per_tick["oxygen"], oxygen_required)