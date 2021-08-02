from unittest.mock import MagicMock
import pytest
from Nodes import Connection, Node


@pytest.fixture
def origin_node():
    return MagicMock(spec = Node.Node)


@pytest.fixture
def target_node():
    return MagicMock(spec = Node.Node)


@pytest.fixture()
def energy_connection(origin_node, target_node) -> Connection.Connection:
    return Connection.Connection(origin_node, target_node, "energy")


# This is some next level pytest magic. This basicly ensures that any test that uses the energy_connection_with_disabled
# fixture is called 3 times. Once where the target is disabled, once where origin is enabled and once more with both
# disabled.
@pytest.fixture(params = [[True, False], [False, True], [False, False]])
def energy_connection_with_disabled(energy_connection, request):
    energy_connection.origin.enabled = request.param[0]
    energy_connection.target.enabled = request.param[1]
    return energy_connection


def test_create(origin_node, target_node):
    # Just don't crash.
   Connection.Connection(origin_node, target_node, "energy")


def test_createUnknownResource(origin_node, target_node):
    with pytest.raises(ValueError):
        Connection.Connection(origin_node, target_node, "zomg")

def test_getReservationDeficiency(origin_node, target_node):
    connection = Connection.Connection(origin_node, target_node, "energy")

    connection.reserved_available_amount = 10
    connection.reserved_requested_amount = 12

    assert connection.getReservationDeficiency() == 2

    connection.reserved_available_amount = 12
    assert connection.getReservationDeficiency() == 0



def test_lock(origin_node, target_node):
    connection = Connection.Connection(origin_node, target_node, "energy")
    assert not connection.locked
    connection.lock()
    assert connection.locked
    assert connection.isReservationStatisfied()  # Locked connections are always statisfied.


def test_reserveResource(energy_connection: Connection.Connection):
    energy_connection.reserveResource(200)

    assert energy_connection.reserved_requested_amount == 200
    assert energy_connection.reserved_available_amount == 0

    # At this point, we asked for 200 (but never checked how much was there). So we have a deficiency of 200
    assert energy_connection.getReservationDeficiency() == 200


def test_getReserveResource(energy_connection: Connection.Connection):
    energy_connection.getResource = MagicMock(return_value = 200)
    energy_connection.reserveResource(300)
    energy_gained = energy_connection.getReservedResource(sub_tick_modifier = 1)

    assert energy_gained == 200  # The get resource returned 200


def test_preGetResource(energy_connection: Connection.Connection):
    energy_connection.origin.preGetResource = MagicMock(return_value = 32)

    # It should be 32, because the origin returns that
    assert energy_connection.preGetResource(20) == 32

    # This function is just a convenience, so ensure that the node get's called right
    energy_connection.origin.preGetResource.assert_called_once_with("energy", 20)


def test_preGetResourceDisabledNode(energy_connection_with_disabled):
    energy_connection_with_disabled.origin.preGetResource = MagicMock(return_value=21)
    assert energy_connection_with_disabled.preGetResource(20) == 0


def test_preGiveResource(energy_connection: Connection.Connection):
    energy_connection.target.preGiveResource = MagicMock(return_value = 32)

    # It should be 32, because the origin returns that
    assert energy_connection.preGiveResource(20) == 32

    # This function is just a convenience, so ensure that the node get's called right
    energy_connection.target.preGiveResource.assert_called_once_with("energy", 20)


def test_preGiveResourceDisabledNode(energy_connection_with_disabled):
    energy_connection_with_disabled.target.preGiveResource = MagicMock(return_value=21)
    assert energy_connection_with_disabled.preGiveResource(2000) == 0


def test_getResource(energy_connection: Connection.Connection):
    energy_connection.origin.getResource = MagicMock(return_value = 900)
    assert energy_connection.getResource(200) == 900
    # Check if the side that got the resources also got their heat "tickled"
    energy_connection.target.addHeat.assert_called_once()


def test_getResourceDisabledNode(energy_connection_with_disabled):
    energy_connection_with_disabled.origin.getResource = MagicMock(return_value=21)
    assert energy_connection_with_disabled.getResource(2000) == 0


def test_giveResource(energy_connection: Connection.Connection):
    energy_connection.target.giveResource = MagicMock(return_value = 9001)
    assert energy_connection.giveResource(300) == 9001
    # check if the target that got the resources got their heat tickled
    energy_connection.target.addHeat.assert_called_once()


def test_giveResourceDisabledNode(energy_connection_with_disabled):
    energy_connection_with_disabled.target.giveResource = MagicMock(return_value=21)
    assert energy_connection_with_disabled.giveResource(2000) == 0


def test_reset(energy_connection: Connection.Connection):
    energy_connection.lock()
    energy_connection.reserveResource(200)
    energy_connection.reserved_available_amount = 12
    energy_connection.reset()
    assert not energy_connection.locked
    assert energy_connection.reserved_requested_amount == 0
    assert energy_connection.reserved_available_amount == 0
