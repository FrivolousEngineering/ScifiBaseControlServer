from unittest.mock import MagicMock

from Nodes import Valve


def test_setPerformance():
    valve = Valve.Valve("omg", "fuel", 10)

    valve.getResourceAvailableThisTick = MagicMock(return_value = 10)

    valve._provideResourceToOutgoingConnections = MagicMock(return_value=5)

    valve._performance = 0.5
    valve._target_performance = 0.5

    valve.preUpdate()
    valve.update()

    valve._provideResourceToOutgoingConnections.assert_called_with("fuel", 5)
