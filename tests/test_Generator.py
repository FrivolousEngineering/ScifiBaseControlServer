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
    assert math.isclose(resources_produced_this_tick["energy"], 15)
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
                                                                                              (1, 4, 0.5)])  # 1 energy left over, but we were running at 50%, so (10 * 0.5 - 1)
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
