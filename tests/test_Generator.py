from unittest.mock import MagicMock

from Nodes import Generator


def test_update():
    generator = Generator.Generator("omg")

    generator._resources_received_this_tick = {"fuel": 20, "water": 0}
    generator._provideResourceToOutogingConnections = MagicMock(return_value = 5)
    generator._getAllReservedResources = MagicMock()
    generator.addHeat = MagicMock()

    generator.update()

    generator.addHeat.assert_called_once()

    assert generator.getResourcesProducedThisTick() == {"energy": 15, "water": 0}
