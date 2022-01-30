import pytest

from Nodes.EnergyBalancer import EnergyBalancer
from Nodes.Node import InvalidConnection, Node
from Nodes.ResourceStorage import ResourceStorage


def test_Connection():
    energy_balancer = EnergyBalancer("balancer")

    battery = ResourceStorage("battery", "energy", 0)

    energy_balancer.connectWith("energy", battery)


def test_InvalidConnection():
    energy_balancer = EnergyBalancer("balancer")

    battery = ResourceStorage("battery", "energy", 0)
    with pytest.raises(InvalidConnection):
        energy_balancer.connectWith("water", battery)


def test_WrongNodeToConnectWith():
    energy_balancer = EnergyBalancer("balancer")

    battery = Node("NotABattery")
    battery._acceptable_resources.add("energy")

    with pytest.raises(InvalidConnection):
        energy_balancer.connectWith("energy", battery)  # Because it's not a resourceStorage!