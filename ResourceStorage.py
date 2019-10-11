from Node import Node
import math


class ResourceStorage(Node):
    def __init__(self, resource_type, amount):
        super().__init__()
        self._resource_type = resource_type
        self._amount = amount
        pass

    def preGetResource(self, resource_type, amount) -> int:
        if resource_type != self._resource_type:
            return 0

        if amount <= self._amount:
            return amount

        return self._amount

    def updateReservations(self):
        print("Updating reservation of", self)
        sorted_reservations = sorted(self._outgoing_connections, key=lambda x: x.reserved_requested_amount, reverse=True)

        reserved_amount = 0
        while len(sorted_reservations):
            max_resources_to_give = (self._amount - reserved_amount) / len(sorted_reservations)
            print("Max resources to give: ", max_resources_to_give)
            active_reservation = sorted_reservations.pop()
            active_reservation.reserved_available_amount = min(max_resources_to_give, active_reservation.reserved_requested_amount)
            print("Resources reserved", active_reservation.reserved_available_amount)
            reserved_amount += active_reservation.reserved_available_amount

    def getResource(self, resource_type, amount) -> int:
        resources_requestable = self.preGetResource(resource_type, amount)
        print("Gained resources %s %s" % (resource_type, resources_requestable))
        self._amount -= resources_requestable
        return resources_requestable

    def preGiveResource(self, resource_type, amount) -> int:
        if resource_type != self._resource_type:
            return 0
        return amount

    def giveResource(self, resource_type, amount) -> int:
        resources_providable = self.preGiveResource(resource_type, amount)

        #Todo; add max amount (eg; "No, the storage is full, stop trying please!")
        self._amount += resources_providable
        print("Gained resources %s %s" % (resource_type, resources_providable))
        return resources_providable