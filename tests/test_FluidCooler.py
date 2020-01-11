from unittest.mock import MagicMock

import pytest
from Nodes import FluidCooler


def test_Update():
    fluid_cooler = FluidCooler.FluidCooler("omg", "water", 10)


    fluid_cooler.getResourceAvailableThisTick = MagicMock(return_value = 200)
    fluid_cooler._provideResourceToOutogingConnections = MagicMock()
    fluid_cooler.update()

    fluid_cooler._provideResourceToOutogingConnections.assert_called_once_with("water", 200)

