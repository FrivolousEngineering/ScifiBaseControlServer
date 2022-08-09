from unittest.mock import MagicMock

from collections import defaultdict
from Nodes import Generator

import math
import pytest


@pytest.fixture
def generator():
    generator = Generator.Generator("omg")
    generator.ensureSaneValues()
    return generator


def test_update(generator):
    generator._resources_received_this_sub_tick = {"fuel": 20, "water": 0}
    generator._provideResourceToOutgoingConnections = MagicMock(return_value = 5)
    generator._getAllReservedResources = MagicMock()
    generator.addHeat = MagicMock()

    # Set the generator at the perfect temperature
    generator._temperature = generator._optimal_temperature
    generator.ensureSaneValues()
    generator.update()

    generator.addHeat.assert_called_once()
    resources_produced_this_tick = generator.getResourcesProducedThisTick()
    resources_provided_this_tick = generator.getResourcesProvidedThisTick()
    assert math.isclose(resources_produced_this_tick["energy"], 200)  # It got 20 fuel, so it created 20 energy
    assert math.isclose(resources_provided_this_tick["energy"], 195)  #  The connection reports that it couldn't dump 5, so 15 was provided
    assert math.isclose(resources_provided_this_tick["water"], 0)

    # Ensure that the an attempt was made to provide energy (20!)
    assert generator._provideResourceToOutgoingConnections.call_args_list[0][0][0] == "energy"
    assert math.isclose(generator._provideResourceToOutgoingConnections.call_args_list[0][0][1], 200)

    # Ensure that an attempt was made to provide water (0!)
    assert generator._provideResourceToOutgoingConnections.call_args_list[1][0][0] == "water"
    assert math.isclose(generator._provideResourceToOutgoingConnections.call_args_list[1][0][1], 0)


def test_generator_resources_left_previous_update(generator):
    generator.deserialize({ "node_id": "omg",
                            "temperature": 200,
                            "resources_received_this_tick": defaultdict(float),
                            "resources_produced_this_tick": defaultdict(float),
                            "resources_left_over": {"energy": 5},
                            "resources_provided_this_tick": defaultdict(float),
                            "resources_required_last_tick": defaultdict(float),
                            "resources_provided_last_tick": defaultdict(float),
                            "resources_produced_last_tick": defaultdict(float),
                            "optional_resources_required_last_tick": defaultdict(float),
                            "optional_resources_required_per_tick": defaultdict(float),
                            "resources_required_per_tick": defaultdict(float),
                            "resources_received_last_tick": defaultdict(float),
                            "original_optional_resources_required_per_tick": defaultdict(float),
                            "stored_heat": 500,
                            "performance": 1,
                            "active": 1,
                            })

    original_resources_available = generator.getResourceAvailableThisTick
    generator.getResourceAvailableThisTick = MagicMock(return_value = 0)

    generator._provideResourceToOutgoingConnections = MagicMock(return_value = 4)

    generator.update()

    # This generator didn't get any resources, but it had resources left (5 energy).
    # Ensure that it attempted to dump that!
    assert generator._provideResourceToOutgoingConnections.call_args_list[0][0][0] == "energy"
    assert generator._provideResourceToOutgoingConnections.call_args_list[0][0][1] == 5

    # Also ensure that it was unable to provide the 4 of the 5 energy it had!
    assert original_resources_available("energy") == 4


def test_update_with_different_energy_factor():
    generator = Generator.Generator("omg", energy_factor=0.25)

    generator._resources_received_this_sub_tick = {"fuel": 20, "water": 0}

    generator._provideResourceToOutgoingConnections = MagicMock(return_value=0)
    generator._getAllReservedResources = MagicMock()
    generator.addHeat = MagicMock()

    # Set the generator at the perfect temperature
    generator._temperature = generator._optimal_temperature
    generator.ensureSaneValues()
    generator.update()

    generator.addHeat.assert_called_once()
    resources_produced_this_tick = generator.getResourcesProducedThisTick()
    resources_provided_this_tick = generator.getResourcesProvidedThisTick()
    assert math.isclose(resources_produced_this_tick["energy"], 5) # 25% of how much fuel was obtained
    assert math.isclose(resources_provided_this_tick["water"], 0)


def test_waterGenerator():
    # Water can't be burned. 
    with pytest.raises(ValueError, match=r"^The provided fuel type \[water\] can't be burned!"):
        Generator.Generator("omg", fuel_type = "water")


def test_oxygenGenerator():
    with pytest.raises(ValueError, match=r"^The provided fuel type \[oxygen\] can't be burned!"):
        Generator.Generator("omg", fuel_type = "oxygen")


@pytest.mark.parametrize("effectiveness_factor, efficiency", [(1, 0.5), (0.5, 0.75), (0.25, 0.875)])
def test_temperature_efficiency(effectiveness_factor, efficiency):
    generator = Generator.Generator("omg")

    generator._getHealthEffectivenessFactor = MagicMock(return_value = effectiveness_factor)

    assert generator.temperature_efficiency == efficiency


@pytest.mark.parametrize("energy_left, fuel_per_tick_required, health_effectiveness_factor", [(1, 0.9, 1),  # One energy left over, so next turn we need 0 (1-1)
                                                                                              (5, 0.5, 1),  # 5 energy left over, so next turn we need 0.5 fuel
                                                                                              (9, 0.1, 1),  # 9 energy left over, so next turn we need 0.1
                                                                                              (1, 0.4, 0.5),  # 1 energy left over, but we were running at 50%,
                                                                                              (11, 0, 1),  # Shouldn't happen; more energy was left than possible. Don't request anything!
                                                                                              ])
def test__update_resources_required_per_tick(energy_left, fuel_per_tick_required, health_effectiveness_factor, generator):
    generator._resources_left_over["energy"] = energy_left
    generator._getHealthEffectivenessFactor = MagicMock(return_value = health_effectiveness_factor)
    generator._updateResourceRequiredPerTick()

    assert math.isclose(generator._resources_required_per_tick["fuel"], fuel_per_tick_required)


def test_setPerformance(generator):
    generator._resources_received_this_tick = {"fuel": 10, "water": 0}
    generator._provideResourceToOutgoingConnections = MagicMock(return_value=0)
    generator._getAllReservedResources = MagicMock()
    generator.addHeat = MagicMock()

    # Set the generator at the perfect temperature
    generator._temperature = generator._optimal_temperature

    assert generator.getResourcesRequiredPerTick()["fuel"] == generator._original_resources_required_per_tick["fuel"]
    generator._min_performance = 0
    # Change the performance
    generator.target_performance = 0.5
    while generator.performance != 0.5:
        generator.preUpdate()
        generator.update()
        assert math.isclose(generator.getResourcesRequiredPerTick()["fuel"], generator._original_resources_required_per_tick["fuel"] * generator.performance)

    # Check that the performance is kept when nothing is changed
    for _ in range(0, 5):
        generator.preUpdate()
        generator.update()
        assert math.isclose(generator.getResourcesRequiredPerTick()["fuel"], generator._original_resources_required_per_tick["fuel"] * generator.performance)

    # Move performance up again!
    generator.target_performance = 0.8
    while generator.performance != 0.8:
        generator.preUpdate()
        generator.update()
        assert math.isclose(generator.getResourcesRequiredPerTick()["fuel"], generator._original_resources_required_per_tick["fuel"] * generator.performance)

    # Check that the performance is kept when nothing is changed
    for _ in range(0, 5):
        generator.preUpdate()
        generator.update()
        assert math.isclose(generator.getResourcesRequiredPerTick()["fuel"], generator._original_resources_required_per_tick["fuel"] * generator.performance)
