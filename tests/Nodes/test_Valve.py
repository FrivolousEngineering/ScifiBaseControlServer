from unittest.mock import MagicMock

from Nodes import Valve


def test_setPerformance():
    valve = Valve.Valve("omg", "fuel", 10)

    valve.getResourceAvailableThisTick = MagicMock(return_value = 10)

    valve._provideResourceToOutgoingConnections = MagicMock(return_value=5)
    assert valve.max_amount_stored == 25

    # Ensure that the _updatePerformance is actually called by having the performance *slightly* different from target
    valve._performance = 0.5001
    valve._target_performance = 0.5

    valve.preUpdate()
    valve.update()

    valve._provideResourceToOutgoingConnections.assert_called_with("fuel", 5)

    assert valve.max_amount_stored == 12.5


def test_preGiveResource_wrongResource():
    valve = Valve.Valve("omg", "fuel", 10)
    assert valve.preGiveResource("water", 100) == 0


def test_preGiveResource_negativeValue():
    valve = Valve.Valve("omg", "fuel", 10)
    assert valve.preGiveResource("fuel", -200) == 0


def test_preGiveResource_extremelySmallAmount():
    # The valve class has some code to check for larger amounts being given to it.
    valve = Valve.Valve("omg", "fuel", 10)
    assert valve.preGiveResource("fuel", 0.0001) == 0.0001


def test_preGiveResource_largeAmount():
    valve = Valve.Valve("omg", "fuel", 10)
    assert valve.preGiveResource("fuel", 200) == 25


def test_preGiveResource_largeAmount_partiallyFilled():
    valve = Valve.Valve("omg", "fuel", 10)
    valve.giveResource("fuel", 10)
    assert valve.preGiveResource("fuel", 200) == 15