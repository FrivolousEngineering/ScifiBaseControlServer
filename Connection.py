from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from Node import Node


class Connection:
    def __init__(self, origin: "Node", target: "Node", resource_type: str) -> None:
        self.origin = origin
        self.target = target
        self.resource_type = resource_type
        self.reserved_requested_amount = 0
        self.reserved_available_amount = 0
        self.locked = False

    def lock(self) -> None:
        self.locked = True
        self.reserved_requested_amount = self.reserved_available_amount

    def reset(self) -> None:
        self.reserved_requested_amount = 0.
        self.reserved_available_amount = 0.
        self.locked = False

    def reserveResource(self, amount: float) -> None:
        self.reserved_requested_amount = amount
        self.reserved_available_amount = 0

    def getReservedResource(self) -> float:
        return self.getResource(self.reserved_requested_amount)

    def isReservationStatisfied(self) -> bool:
        # If a reservation is locked it can't be used to get more.
        return self.reserved_requested_amount <= self.reserved_available_amount or self.locked

    def getReservationDeficiency(self) -> float:
        return self.reserved_requested_amount - self.reserved_available_amount

    def getResource(self, amount: float) -> float:
        return self.origin.getResource(self.resource_type, amount)

    def preGetResource(self, amount: float) -> float:
        return self.origin.preGetResource(self.resource_type, amount)

    def giveResource(self, amount: float) -> float:
        return self.target.giveResource(self.resource_type, amount)

    def preGiveResource(self, amount: float) -> float:
        return self.target.preGiveResource(self.resource_type, amount)

    def __repr__(self):
        return "{resource_type} connection between {origin} and {target}".format(origin = self.origin,
                                                                                 target = self.target,
                                                                                 resource_type = self.resource_type)