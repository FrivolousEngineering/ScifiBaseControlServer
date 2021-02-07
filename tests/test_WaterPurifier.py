from unittest.mock import MagicMock
import math

import pytest

from Nodes import WaterPurifier


@pytest.mark.parametrize("resources_received,                   resources_produced",
                        [({"dirty_water": 10},                  {"water": 5, "animal_waste": 5}),
                         ({"dirty_water": 10, "oxygen": 10},    {"water": 10, "animal_waste": 10}),
                         ({"dirty_water": 10, "oxygen": 5},     {"water": 7.5, "animal_waste": 7.5}),
                         ({"dirty_water": 7.5, "oxygen": 10},   {"water": 7.5, "animal_waste": 7.5}),
                         ({"oxygen": 10},                       {"water": 0, "animal_waste": 0})])
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
    assert purifier._provideResourceToOutgoingConnections.call_args_list[1][0][0] == "animal_waste"
    assert math.isclose(purifier._provideResourceToOutgoingConnections.call_args_list[1][0][1], resources_produced["animal_waste"])



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
    water_purifier._resources_left_over["animal_waste"] = waste_left
    water_purifier._resources_left_over["water"] = water_left
    water_purifier._getHealthEffectivenessFactor = MagicMock(return_value = health_effectiveness_factor)
    water_purifier._updateResourceRequiredPerTick()
    calculated_resources_required = water_purifier.getAllResourcesRequiredPerTick()
    assert math.isclose(calculated_resources_required["dirty_water"], dirty_water_required)
    assert math.isclose(calculated_resources_required["oxygen"], oxygen_required)


def test_purifier_resources_left_previous_update():
    water_purifier = WaterPurifier.WaterPurifier("omg")
    water_purifier.deserialize({"node_id": "omg", "temperature": 200, "resources_received_this_tick": {},
                      "resources_produced_this_tick": {}, "resources_left_over": {"animal_waste": 5, "water": 3}})

    original_resources_available = water_purifier.getResourceAvailableThisTick
    water_purifier.getResourceAvailableThisTick = MagicMock(return_value = 0)

    water_purifier._provideResourceToOutgoingConnections = MagicMock(return_value = 4)

    water_purifier.update()

    # This generator didn't get any resources, but it had resources left (5 water)
    # Ensure that it attempted to dump that!
    assert water_purifier._provideResourceToOutgoingConnections.call_args_list[0][0][0] == "water"
    assert water_purifier._provideResourceToOutgoingConnections.call_args_list[0][0][1] == 3

    # Ensure that an attempt was made to provide waste (3!)
    assert water_purifier._provideResourceToOutgoingConnections.call_args_list[1][0][0] == "animal_waste"
    assert math.isclose(water_purifier._provideResourceToOutgoingConnections.call_args_list[1][0][1], 5)

    # Also ensure that it was unable to provide the 4 of the 5 energy it had!
    assert original_resources_available("water") == 4