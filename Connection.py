from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from Node import Node


class Connection:
    def __init__(self, origin: "Node", target: "Node", resource_type):
        self.origin = origin
        self.target = target
        self.resource_type = resource_type
        self.reserved_requested_amount = 0
        self.reserved_available_amount = 0
        self.locked = False

    def lock(self):
        self.locked = True
        self.reserved_requested_amount = self.reserved_available_amount

    def reset(self):
        self.reserved_requested_amount = 0
        self.reserved_available_amount = 0

    def reserveResource(self, amount):
        self.reserved_requested_amount = amount
        self.reserved_available_amount = 0

    def isReservationStatisfied(self):
        # If a reservation is locked it can't be used to get more.
        return self.reserved_requested_amount <= self.reserved_available_amount or self.locked

    def getReservationDeficiency(self):
        return self.reserved_requested_amount - self.reserved_available_amount

    def getResource(self, amount):
        return self.origin.getResource(self.resource_type, amount)

    def preGetResource(self, amount):
        return self.origin.preGetResource(self.resource_type, amount)

    def giveResource(self, amount):
        return self.target.giveResource(self.resource_type, amount)

    def preGiveResource(self, amount):
        return self.target.preGiveResource(self.resource_type, amount)