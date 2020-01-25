from unittest.mock import MagicMock
import math
from Nodes import Generator


def test_update():
    generator = Generator.Generator("omg")

    generator._resources_received_this_tick = {"fuel": 20, "water": 0}
    generator._provideResourceToOutogingConnections = MagicMock(return_value = 5)
    generator._getAllReservedResources = MagicMock()
    generator.addHeat = MagicMock()

    generator.update()

    generator.addHeat.assert_called_once()
    resources_produced_this_tick = generator.getResourcesProducedThisTick()
    assert math.isclose(resources_produced_this_tick["energy"], 15)
    assert math.isclose(resources_produced_this_tick["water"], 0)