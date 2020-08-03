from unittest.mock import MagicMock

from Nodes import Node
from Nodes.Modifiers import Modifier
import pytest

from Nodes.Constants import WEIGHT_PER_UNIT


@pytest.fixture
def node_energy_left():
    node = Node.Node("zomg")
    node._resources_left_over["energy"] = 10
    return node


def createConnection(is_statisfied, reservation_deficiency, pre_give_result = 0):
    connection = MagicMock()
    connection.isReservationStatisfied = MagicMock(return_value=is_statisfied)
    connection.getReservationDeficiency = MagicMock(return_value=reservation_deficiency)
    connection.preGiveResource = MagicMock(return_value = pre_give_result)
    connection.giveResource = MagicMock(return_value=pre_give_result)
    connection.reserved_requested_amount = 0
    return connection


def test_getId():
    node = Node.Node("zomg")
    assert node.getId() == "zomg"


def test_enabled():
    node = Node.Node("zomg")
    assert node.enabled

    node.enabled = False
    assert not node.enabled


def test_repair():
    node = Node.Node("zomg")

    node._health = 20

    node.repair(100)
    assert node.health == 100


def test_negativeRepair():
    node = Node.Node("zomg")
    node.repair(-200)
    assert node.health == 100


def test_addHeat():
    node = Node.Node("yay")

    starting_temp = node.temperature
    node.addHeat(300)
    assert node.temperature == starting_temp + 1


def test_connect():
    node_1 = Node.Node("zomg")
    node_2 = Node.Node("omg")

    node_1.connectWith("energy", node_2)

    assert len(node_1.getAllOutgoingConnectionsByType("energy")) == 1
    assert len(node_2.getAllIncomingConnectionsByType("energy")) == 1


@pytest.mark.parametrize("starting_temperature, outside_temperature, heat_emitted", [(0, 0, 0),
                                                                                     (200, 200, 0),
                                                                                     (201, 200, -0.91402670835),
                                                                                     (200, 201, 0.91402670835),
                                                                                     (200, 202, 1.8417978936)])
def test__emitHeat(starting_temperature, outside_temperature, heat_emitted):
    node = Node.Node("")
    node.addHeat = MagicMock()
    node.outside_temp = outside_temperature

    # Force the starting temperature
    node._temperature = starting_temperature

    node._emitHeat()

    node.addHeat.assert_called_with(heat_emitted)


@pytest.mark.parametrize("starting_temperature, outside_temperature, heat_emitted", [(0, 0, 0),
                                                                                     (200, 200, 0),
                                                                                     (201, 200, -10),
                                                                                     (200, 201, 10),
                                                                                     (200, 202, 20)])
def test__convectiveHeatTransfer(starting_temperature, outside_temperature, heat_emitted):
    node = Node.Node("")
    node.addHeat = MagicMock()
    node.outside_temp = outside_temperature
    # Force the starting temperature
    node._temperature = starting_temperature

    node._convectiveHeatTransfer()
    node.addHeat.assert_called_with(heat_emitted)


def test_requiresReplanningNoConnections():
    node = Node.Node("")
    assert not node.requiresReplanning()


def test_requiresReplanningAllConnectionsStatisfied():
    node = Node.Node("")
    node.addConnection(MagicMock(isReservationStatisfied = MagicMock(return_value = True)))
    assert not node.requiresReplanning()


def test_requiresReplanningOneConnectionStatisified():
    node = Node.Node("")
    node.addConnection(MagicMock(isReservationStatisfied=MagicMock(return_value=True)))
    node.addConnection(MagicMock(isReservationStatisfied=MagicMock(return_value=False)))

    assert node.requiresReplanning()


def test_getResourceAvailableThisTick(node_energy_left):
    # The node had 10 resources left over. So even though nothing was requested, it should report 10.
    assert node_energy_left.getResourceAvailableThisTick("energy") == 10

    node_energy_left.getResourcesReceivedThisTick()["energy"] = 50

    assert node_energy_left.getResourceAvailableThisTick("energy") == 60


def test_postUpdate(node_energy_left):
    mocked_node = MagicMock()
    node_energy_left.getResourcesProducedThisTick()["fuel"] = 20
    node_energy_left.connectWith("water", mocked_node)

    connection = node_energy_left.getAllOutgoingConnectionsByType("water")[0]
    connection.reset = MagicMock()
    node_energy_left.postUpdate()

    connection.reset.assert_called_once()
    # After the post update, things get resetted again, so it should report 0!
    assert node_energy_left.getResourcesReceivedThisTick() == {}
    assert node_energy_left.getResourcesProducedThisTick() == {}


def test__getAllReservedResources():
    node = Node.Node("")
    node.getResourcesRequiredPerTick()["water"] = 10
    node._getReservedResourceByType = MagicMock()
    node._getAllReservedResources()
    node._getReservedResourceByType.assert_called_once_with("water")


def test__getReservedResourceByType():
    node = Node.Node("")
    connection = MagicMock()
    connection.getReservedResource = MagicMock(return_value = 209)
    node.getAllIncomingConnectionsByType = MagicMock(return_value = [connection])

    assert node._getReservedResourceByType("zomg") == 209


def test_replanReservations():
    node = Node.Node("")
    node.getResourcesRequiredPerTick()["water"] = 10
    connection_1 = createConnection(False, 20)
    connection_2 = createConnection(True, 0)

    node.getAllIncomingConnectionsByType = MagicMock(return_value=[connection_1, connection_2])

    node.replanReservations()

    connection_1.lock.assert_called_once()
    connection_2.reserveResource.assert_called_once_with(20)


def test_replanReservationsNoDefficiency():
    node = Node.Node("")
    node.getResourcesRequiredPerTick()["water"] = 10
    connection_1 = createConnection(False, 0)
    connection_2 = createConnection(True, 0)

    node.getAllIncomingConnectionsByType = MagicMock(return_value=[connection_1, connection_2])

    node.replanReservations()

    connection_1.lock.assert_called_once()
    connection_2.lock.assert_called_once()


def test_replanReservationsNoStatisfied():
    node = Node.Node("")
    node.getResourcesRequiredPerTick()["water"] = 10
    connection_1 = createConnection(False, 0)
    connection_2 = createConnection(False, 0)

    node.getAllIncomingConnectionsByType = MagicMock(return_value=[connection_1, connection_2])

    node.replanReservations()

    connection_1.lock.assert_called_once()
    connection_2.lock.assert_called_once()


def test_preUpdate():
    node = Node.Node("")
    node.getResourcesRequiredPerTick()["energy"] = 10
    connection_1 = createConnection(False, 0)
    connection_2 = createConnection(False, 0)

    node.getAllIncomingConnectionsByType = MagicMock(return_value=[connection_1, connection_2])
    node.preUpdate()
    
    # Each of the connections should be asked for half of what we requested
    connection_1.reserveResource.assert_called_once_with(5)
    connection_2.reserveResource.assert_called_once_with(5)


@pytest.mark.parametrize("connections, amount_to_provide, resources_left", [([createConnection(True, 0), createConnection(True, 0)], 20, 20),
                                                                    ([createConnection(True, 0, 12), createConnection(True, 0, 3)], 15, 0),
                                                                    ([createConnection(True, 0, 12), createConnection(True, 0, 0)], 18, 6),
                                                                    ([createConnection(True, 0, 12), createConnection(True, 0, 0), createConnection(True, 0, 3)], 18, 3),
                                                                    ])
def test_provideResourceToOutogingConnections(connections, amount_to_provide, resources_left):
    node = Node.Node("")

    node.getAllOutgoingConnectionsByType = MagicMock(return_value = connections)

    assert node._provideResourceToOutogingConnections("fuel", amount_to_provide) == resources_left


@pytest.mark.parametrize("resource_type", WEIGHT_PER_UNIT.keys())
def test_simpleGetters(resource_type):
    # It's not really a test, but the results should remain the same, as other child nodes depend on this
    # implementation. Call them with all resources types known to us.
    node = Node.Node("")
    assert node.preGetResource(resource_type, 200) == 0
    assert node.preGiveResource(resource_type, 200) == 0
    assert node.getResource(resource_type, 200) == 0
    assert node.giveResource(resource_type, 200) == 0


def test_update():
    node = Node.Node("")
    node.updateCalled.emit = MagicMock()

    node.update()

    node.updateCalled.emit.assert_called_once_with(node)


def test_serialize():
    node = Node.Node("zomg")

    serialized = node.serialize()

    assert serialized["node_id"] == node.getId()
    assert serialized["temperature"] == node.temperature


def test_deserialize():
    node = Node.Node("BLOOORPP")

    node.deserialize({"node_id": "omgzomg", "temperature": 200, "resources_received_this_tick": {}, "resources_produced_this_tick": {}, "resources_left_over": {}})

    assert node.getId() == "omgzomg"
    assert node.temperature == 200


def test_releaseLock():
    node = Node.Node("BLOOORPP")
    # We should be allowed to release a lock multiple times, yay!
    node.releaseUpdateLock()
    node.releaseUpdateLock()


def test_nodePerformance():
    node = Node.Node("SuchNode!")
    node._min_performance = 0.5
    node._max_performance = 1.5

    assert node.target_performance == 1

    node.target_performance = 200
    assert node.target_performance == 1.5

    node.target_performance = 0
    assert node.target_performance == 0.5


def test_ZeroPerformance():
    # Ensure that we can set the performance to 0 and back again.
    node = Node.Node("SuchNode!")
    node._min_performance = 0
    node._resources_required_per_tick["water"] = 10
    assert node.getResourcesRequiredPerTick()["water"] == 10

    node._target_performance = 0
    node._updatePerformance()
    assert node.getResourcesRequiredPerTick()["water"] == 0

    node._target_performance = 0.5
    node._updatePerformance()
    assert node.getResourcesRequiredPerTick()["water"] == 5


def test_modifier():
    node = Node.Node("ModifiedNode")
    modifier = MagicMock(spec=Modifier.Modifier)

    node.addModifier(modifier)

    assert modifier in node.getModifiers()

    node.removeModifier(modifier)
    assert modifier not in node.getModifiers()

    # Removing a modifier that is not in the list should cause no issues
    node.removeModifier(modifier)
