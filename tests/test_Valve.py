from unittest.mock import MagicMock

from Nodes import Valve


def test_setPerformance():
    valve = Valve.Valve("omg", "fuel", 10)

    valve.getResourceAvailableThisTick = MagicMock(return_value = 10)

    valve._provideResourceToOutgoingConnections = MagicMock(return_value=5)
    assert valve.max_amount_stored == 20

    # Ensure that the _updatePerformance is actually called by having the performance *slightly* different from target
    valve._performance = 0.5001
    valve._target_performance = 0.5

    valve.preUpdate()
    valve.update()

    valve._provideResourceToOutgoingConnections.assert_called_with("fuel", 5)

    assert valve.max_amount_stored == 10

