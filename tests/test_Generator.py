from unittest.mock import MagicMock
import math

import pytest

from Nodes import Generator


def test_update():
    generator = Generator.Generator("omg")

    generator._resources_received_this_tick = {"fuel": 20, "water": 0}
    generator._provideResourceToOutgoingConnections = MagicMock(return_value = 5)
    generator._getAllReservedResources = MagicMock()
    generator.addHeat = MagicMock()

    # Set the generator at the perfect temperature
    generator._temperature = generator._optimal_temperature

    generator.update()

    generator.addHeat.assert_called_once()
    resources_produced_this_tick = generator.getResourcesProducedThisTick()
    assert math.isclose(resources_produced_this_tick["energy"], 15) # 20 fuel, 5 energy was provided, so 15 left
    assert math.isclose(resources_produced_this_tick["water"], 0)


    # Ensure that the an attempt was made to provide energy (20!)
    assert generator._provideResourceToOutgoingConnections.call_args_list[0][0][0] == "energy"
    assert math.isclose(generator._provideResourceToOutgoingConnections.call_args_list[0][0][1], 20)

    # Ensure that an attempt was made to provide water (0!)
    assert generator._provideResourceToOutgoingConnections.call_args_list[1][0][0] == "water"
    assert math.isclose(generator._provideResourceToOutgoingConnections.call_args_list[1][0][1], 0)

    assert math.isclose(generator.addHeat.call_args[0][0], 75000) # 20 fuel, 7500 combustion heat, 50% effiency


def test_generator_resources_left_previous_update():
    generator = Generator.Generator("omg")
    generator.deserialize({"node_id": "omg", "temperature": 200, "resources_received_this_tick": {},
                      "resources_produced_this_tick": {}, "resources_left_over": {"energy": 5}})

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

    generator._resources_received_this_tick = {"fuel": 20, "water": 0}

    generator._provideResourceToOutgoingConnections = MagicMock(return_value=0)
    generator._getAllReservedResources = MagicMock()
    generator.addHeat = MagicMock()

    # Set the generator at the perfect temperature
    generator._temperature = generator._optimal_temperature

    generator.update()

    generator.addHeat.assert_called_once()
    resources_produced_this_tick = generator.getResourcesProducedThisTick()
    assert math.isclose(resources_produced_this_tick["energy"], 5) # 25% of how much fuel was obtained
    assert math.isclose(resources_produced_this_tick["water"], 0)


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


@pytest.mark.parametrize("energy_left, fuel_per_tick_required, health_effectiveness_factor", [(1, 9, 1),  # One energy left over, so next turn we need 9 (10-1)
                                                                                              (5, 5, 1),  # 5 energy left over, so next turn we need 5 fuel (10-5)
                                                                                              (9, 1, 1),  # 9 energy left over, so next turn we need 1 fuel (10 - 9)
                                                                                              (1, 4, 0.5),  # 1 energy left over, but we were running at 50%, so (10 * 0.5 - 1)
                                                                                              (11, 0, 1),  # Shouldn't happen; more energy was left than possible. Don't request anything!
                                                                                              ])
def test__update_resources_required_per_tick(energy_left, fuel_per_tick_required, health_effectiveness_factor):
    generator = Generator.Generator("omg")
    generator._resources_left_over["energy"] = energy_left
    generator._getHealthEffectivenessFactor = MagicMock(return_value = health_effectiveness_factor)
    generator._updateResourceRequiredPerTick()

    assert math.isclose(generator._resources_required_per_tick["fuel"], fuel_per_tick_required)


def test_setPerformance():
    generator = Generator.Generator("omg")

    generator._resources_received_this_tick = {"fuel": 10, "water": 0}
    generator._provideResourceToOutgoingConnections = MagicMock(return_value=0)
    generator._getAllReservedResources = MagicMock()
    generator.addHeat = MagicMock()

    # Set the generator at the perfect temperature
    generator._temperature = generator._optimal_temperature

    # Ensure that the default that it's requesting is 10
    assert generator.getResourcesRequiredPerTick()["fuel"] == 10
    generator._min_performance = 0
    # Change the performance
    generator.target_performance = 0.5
    while generator.performance != 0.5:
        generator.preUpdate()
        generator.update()
        assert math.isclose(generator.getResourcesRequiredPerTick()["fuel"], 10 * generator.performance)

    # Check that the performance is kept when nothing is changed
    for _ in range(0, 5):
        generator.preUpdate()
        generator.update()
        assert math.isclose(generator.getResourcesRequiredPerTick()["fuel"], 10 * generator.performance)

    # Move performance up again!
    generator.target_performance = 0.8
    while generator.performance != 0.8:
        generator.preUpdate()
        generator.update()
        assert math.isclose(generator.getResourcesRequiredPerTick()["fuel"], 10 * generator.performance)

    # Check that the performance is kept when nothing is changed
    for _ in range(0, 5):
        generator.preUpdate()
        generator.update()
        assert math.isclose(generator.getResourcesRequiredPerTick()["fuel"], 10 * generator.performance)
