import pytest
import ResourceStorage


get_list = [(20,    0,      "energy"),  # Wrong resource type
            (20,    20,     "water"),
            (3.7,   3.7,    "water"),
            (9001,  20,     "water"),
            (-20,   0,      "water")]

give_list = [(20,   0,  None,   "energy"),
             (20,   20, None,   "water"),
             (99,   99, None,   "water"),
             (5,    1,  21,     "water"),
             (-20,  0,  200,    "water"),
             (20,   20, 9000,   "water")]


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