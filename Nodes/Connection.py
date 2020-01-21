from typing import TYPE_CHECKING
from Nodes.Constants import SPECIFIC_HEAT, WEIGHT_PER_UNIT
if TYPE_CHECKING:
    from Nodes.Node import Node


class Connection:
    """
    Connections are one directional links that enable resources to be transported from one Node to another Node.
    """
    def __init__(self, origin: "Node", target: "Node", resource_type: str) -> None:
        """
        Connections are one directional links that enable resources to be transported from one node to another.

        :param origin: The node from which the resources can be requested
        :param target: The node that will receive the resources
        :param resource_type: The type of the resources that this connection transports.
        """
        self.origin = origin
        self.target = target
        self.resource_type = resource_type.lower()
        self.reserved_requested_amount = 0.
        self.reserved_available_amount = 0.
        self.locked = False
        try:
            self._specific_heat = SPECIFIC_HEAT[self.resource_type]
            self._weight_per_unit = WEIGHT_PER_UNIT[self.resource_type]
        except KeyError:
            raise ValueError("Resource type %s was not recognised. Did you forget to add it to the constants file?" %
                             self.resource_type)

    def lock(self) -> None:
        """
        Locking a connection is done during the reserve stage. Once a node can't provide any more resources, it will
        lock all of it's outgoing connections.
        """
        self.locked = True
        self.reserved_requested_amount = self.reserved_available_amount

    def reset(self) -> None:
        """
        Reset the status of the connection. This should be done once a tick is completed.
        """
        self.reserved_requested_amount = 0.
        self.reserved_available_amount = 0.
        self.locked = False

    def reserveResource(self, amount: float) -> None:
        """
        Reserving resources must be done before the update. This will ensure that the origin node will know how much
        resources the target node(s) want to have.

        :param amount: The amount of resources to reserve.
        :return:
        """
        self.reserved_requested_amount = amount
        self.reserved_available_amount = 0

    def getReservedResource(self) -> float:
        """
        Convenience function to actually get (eg; subtract) the amount from the origin.

        :return: The amount it was actually able to get. If the planning was correct, it should be the same as what was
                 reserved.
        """
        return self.getResource(self.reserved_available_amount)

    def isReservationStatisfied(self) -> bool:
        """
        Check if the reservation was statisfied. This can be because enough resources are available or when reservation
        is locked (aka; it can't be used to get more)

        :return:
        """
        return self.reserved_requested_amount <= self.reserved_available_amount or self.locked

    def getReservationDeficiency(self) -> float:
        """
        Get the difference between what was reserved and what is available.

        :return: The difference
        """
        return self.reserved_requested_amount - self.reserved_available_amount

    def getResource(self, amount: float) -> float:
        if not self.origin.enabled or not self.target.enabled:
            return 0
        result = self.origin.getResource(self.resource_type, amount)
        # The heat of the target needs to be changed, but we have to make it act as if this already happend (hence the
        # extra parameter to account for this)
        self.target.addHeat(result * (self.origin.temperature - self.target.temperature) * self._specific_heat,
                            -amount * self._weight_per_unit)
        return result

    def preGetResource(self, amount: float) -> float:
        if not self.origin.enabled or not self.target.enabled:
            return 0
        return self.origin.preGetResource(self.resource_type, amount)

    def giveResource(self, amount: float) -> float:
        if not self.origin.enabled or not self.target.enabled:
            return 0
        result = self.target.giveResource(self.resource_type, amount)
        # The heat of the target needs to be changed, but we have to make it act as if this already happend (hence the
        # extra parameter to account for this)
        self.target.addHeat(result * (self.origin.temperature - self.target.temperature) * self._specific_heat,
                            amount * self._weight_per_unit)
        if self.target.getId() == "fluid_cooler_1":
            print("addedHEAT:", result * (self.origin.temperature - self.target.temperature) * self._specific_heat, self.origin.getId())
        return result

    def preGiveResource(self, amount: float) -> float:
        if not self.origin.enabled or not self.target.enabled:
            return 0
        return self.target.preGiveResource(self.resource_type, amount)

    def __repr__(self) -> str:
        return "{resource_type} connection between {origin} and {target}".format(origin = self.origin,
                                                                                 target = self.target,
                                                                                 resource_type = self.resource_type)
