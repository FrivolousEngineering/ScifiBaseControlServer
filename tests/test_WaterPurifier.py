from unittest.mock import MagicMock
import math

import pytest

from Nodes import WaterPurifier
from collections import defaultdict

from tests.testHelpers import createEngineFromConfig


@pytest.fixture
def water_purifier():
    purifier = WaterPurifier.WaterPurifier("omg")
    purifier.ensureSaneValues()
    return purifier


@pytest.mark.parametrize(
"""resources_received,                    resources_produced""",[
   ({"dirty_water": 10},                  {"water": 5, "animal_waste": 0.5}),
   ({"dirty_water": 10, "oxygen": 140},   {"water": 10, "animal_waste": 1}),
   ({"dirty_water": 10, "oxygen": 70},    {"water": 7.5, "animal_waste": 0.75}),
   ({"dirty_water": 7.5, "oxygen": 140},  {"water": 7.5, "animal_waste": 0.75}),
   ({"oxygen": 140},                      {"water": 0, "animal_waste": 0}),
   ({"oxygen": 20},                       {"water": 0, "animal_waste": 0})])
def test_update(resources_received, resources_produced, water_purifier):
    water_purifier._resources_received_this_sub_tick = resources_received
    water_purifier._provideResourceToOutgoingConnections = MagicMock(return_value = 0)
    water_purifier._getAllReservedResources = MagicMock()

    water_purifier._temperature = water_purifier._optimal_temperature

    water_purifier.update()

    resources_produced_this_tick = water_purifier.getResourcesProducedThisTick()

    for key in resources_produced:
        assert math.isclose(resources_produced_this_tick[key], resources_produced[key]), "%s doesn't match" % key

    # Ensure that the an attempt was made to provide energy (20!)
    assert water_purifier._provideResourceToOutgoingConnections.call_args_list[0][0][0] == "water"
    assert math.isclose(water_purifier._provideResourceToOutgoingConnections.call_args_list[0][0][1], resources_produced["water"])

    # Ensure that an attempt was made to provide water (0!)
    assert water_purifier._provideResourceToOutgoingConnections.call_args_list[1][0][0] == "animal_waste"
    assert math.isclose(water_purifier._provideResourceToOutgoingConnections.call_args_list[1][0][1], resources_produced["animal_waste"])


@pytest.mark.parametrize(
""" waste_left,   water_left, oxygen_required,  dirty_water_required,   health_effectiveness_factor""", [
    (0.1,         9,          14,               1,                      1),
    (0.9,         1,          14,               1,                      1),
    (0,           0,          140,              10,                     1),
    (0,           0,          70,               5,                      0.5),
    (0.3,         3,          28,               2,                      0.5),
    (0.8,         2,          0,                0,                      0.5),  # More left than needed!
    (0.1,         1,          14,               1,                      0.2)])
def test__update_resources_required_per_tick(waste_left, water_left, oxygen_required, dirty_water_required,
                                             health_effectiveness_factor, water_purifier):
    water_purifier._resources_left_over["animal_waste"] = waste_left
    water_purifier._resources_left_over["water"] = water_left
    water_purifier._getHealthEffectivenessFactor = MagicMock(return_value = health_effectiveness_factor)
    water_purifier._updateResourceRequiredPerTick()
    calculated_resources_required = water_purifier.getAllResourcesRequiredPerTick()
    assert math.isclose(calculated_resources_required["dirty_water"], dirty_water_required)
    assert math.isclose(calculated_resources_required["oxygen"], oxygen_required)


def test_purifier_resources_left_previous_update(water_purifier):
    water_purifier.deserialize({
                                    "node_id": "omg",
                                    "temperature": 200,
                                    "resources_received_this_tick": defaultdict(float),
                                    "resources_produced_this_tick": defaultdict(float),
                                    "resources_provided_this_tick": defaultdict(float),
                                    "resources_left_over":
                                    {
                                        "animal_waste": 5,
                                        "water": 3
                                    }
                                })

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


@pytest.mark.parametrize("config_file", ["WaterPurifierSetup.json", "WaterPurifierWithOxygenSetup.json"])
def test_sameTemperature(config_file):
    engine = createEngineFromConfig(config_file)
    engine._sub_ticks = 1
    purifier = engine.getNodeById("purifier")
    begin_temp = purifier.temperature
    engine.doTick()
    assert math.isclose(purifier.temperature, begin_temp)


@pytest.mark.parametrize("sub_ticks", [1, 10, 30])
@pytest.mark.parametrize('ticks', [1, 10, 20])
@pytest.mark.parametrize("config_file, clean_water_produced_per_tick", [("WaterPurifierSetup.json", 5), ("WaterPurifierWithOxygenSetup.json", 10)])
def test_plantsProduced(config_file, clean_water_produced_per_tick, sub_ticks, ticks):
    engine = createEngineFromConfig(config_file)
    engine._sub_ticks = sub_ticks
    for _ in range(ticks):
        engine.doTick()

    assert math.isclose(engine.getNodeById("water_storage").amount_stored, clean_water_produced_per_tick * ticks)