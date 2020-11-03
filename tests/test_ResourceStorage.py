from unittest.mock import MagicMock

import pytest
from Nodes import ResourceStorage, Node

get_list = [(20,    0,      "energy"),  # Wrong resource type
            (20,    20,     "water"),
            (0,     0,      "water"),  # Not giving anything work
            (0.9,   0.9,    "water"),
            (9001,  20,     "water"),
            (-20,   0,      "water")]

give_list = [(20,   0,      None,   "energy"),
             (20,   20,     None,   "water"),
             (0.9,  0.9,    None,   "water"),
             (5,    1,      21,     "water"),
             (-20,  0,      200,    "water"),
             (20,   20,     9000,   "water")]


@pytest.mark.parametrize("requested, gained, resource_type", get_list)
def test_preGetResource(requested, gained, resource_type):
    storage = ResourceStorage.ResourceStorage("", "water", 20)

    assert storage.preGetResource(resource_type, requested) == gained


@pytest.mark.parametrize("requested, gained, resource_type", get_list)
def test_getResource(requested, gained, resource_type):
    storage = ResourceStorage.ResourceStorage("", "water", 20)

    assert storage.getResource(resource_type, requested) == gained
    assert storage._amount == 20 - gained


@pytest.mark.parametrize("requested, stored, max_storage, resource_type", give_list)
def test_preGiveResource(requested, stored, max_storage, resource_type):
    storage = ResourceStorage.ResourceStorage("", "water", 20, max_storage)

    assert storage.preGiveResource(resource_type, requested) == stored


@pytest.mark.parametrize("requested, stored, max_storage, resource_type", give_list)
def test_giveResource(requested, stored, max_storage, resource_type):
    storage = ResourceStorage.ResourceStorage("", "water", 20, max_storage)

    assert storage.giveResource(resource_type, requested) == stored
    assert storage._amount == 20 + stored


def test_giveResourceTwice():
    storage = ResourceStorage.ResourceStorage("", "water", 20)
    storage.giveResource("water", 10)
    storage.giveResource("water", 20)
    assert storage.amount_stored == 50

    assert storage.getResourcesReceivedThisTick() == {"water": 30}

@pytest.mark.parametrize("requested, received", [([20, 21], [10, 10]),
                                                 ([5, 9],   [5, 9]),
                                                 ([6, 6, 8], [6, 6, 8]),
                                                 ([200, 6, 6], [8, 6, 6]),
                                                 ([200, 200, 200, 200], [5, 5, 5, 5])
                                                 ])
def test_updateReservations(requested, received):
    storage = ResourceStorage.ResourceStorage("", "energy", 20)
    connections = []
    for request in requested:
        connections.append(MagicMock(reserved_requested_amount = request))

    storage.getAllOutgoingConnectionsByType = MagicMock(return_value = connections)
    storage.updateReservations()

    for idx, received in enumerate(received):
        assert connections[idx].reserved_available_amount == received


def test_deserialize():
    storage = ResourceStorage.ResourceStorage("", "energy", 20)
    assert storage.amount_stored == 20

    storage.deserialize({'node_id': '', 'resources_received_this_tick': {}, 'resources_produced_this_tick': {}, 'resources_left_over': {}, 'temperature': 293.15, 'amount_stored': 120})
    assert storage.amount_stored == 120


def test_serialize():
    storage = ResourceStorage.ResourceStorage("", "energy", 291)
    assert storage.serialize()["amount_stored"] == 291


def test_weight_energy():
    storage = ResourceStorage.ResourceStorage("", "energy", 20)
    storage_2 = ResourceStorage.ResourceStorage("", "energy", 500)
    # Energy storage should always be the same weight as eachoter (because energy doesn't have extra weight.
    assert storage.weight == storage_2.weight


def test_weight_water():
    energy_store = ResourceStorage.ResourceStorage("", "energy", 20)
    water_store = ResourceStorage.ResourceStorage("", "water", 20)
    assert water_store.weight > energy_store.weight


def test_max_storage():
    storage = ResourceStorage.ResourceStorage("", "energy", 20)
    assert storage.max_amount_stored == -1

    storage_with_max = ResourceStorage.ResourceStorage("", "energy", 20, max_storage= 200)
    assert storage_with_max.max_amount_stored == 200
