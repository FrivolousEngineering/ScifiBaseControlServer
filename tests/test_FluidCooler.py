from unittest.mock import MagicMock

from Nodes import FluidCooler


def test_Update():
    fluid_cooler = FluidCooler.FluidCooler("omg", "water", 10)

    fluid_cooler.getResourceAvailableThisTick = MagicMock(return_value = 200)
    fluid_cooler._provideResourceToOutogingConnections = MagicMock(return_value = 10)
    fluid_cooler.update()
    # First time round it's going to provide 0 water, since it's keeping all stuff inside for one tick
    fluid_cooler._provideResourceToOutogingConnections.assert_called_once_with("water", 0)

    fluid_cooler._provideResourceToOutogingConnections.reset_mock()
    fluid_cooler.update()
    fluid_cooler._provideResourceToOutogingConnections.assert_called_once_with("water", 210)

