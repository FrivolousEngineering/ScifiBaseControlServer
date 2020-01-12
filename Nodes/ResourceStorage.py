from typing import Optional

from Nodes.Node import Node
from Nodes.Constants import WEIGHT_PER_UNIT


class ResourceStorage(Node):
    def __init__(self, node_id: str, resource_type: str, amount: float, max_storage: Optional[float] = None, **kwargs):
        super().__init__(node_id, **kwargs)
        self._resource_type = resource_type.lower()
        self._amount = amount
        self._max_storage = max_storage
        self._resource_weight_per_unit = WEIGHT_PER_UNIT[self._resource_type]

    @property
    def amount_stored(self):
        return self._amount

    @property
    def weight(self):
        return self._weight + self._resource_weight_per_unit * self._amount

    def preGetResource(self, resource_type: str, amount: float) -> float:
        if resource_type != self._resource_type:
            return 0
        if amount < 0:
            return 0
        if amount <= self._amount:
            return amount

        return self._amount

    def updateReservations(self) -> None:
        sorted_reservations = sorted(self._outgoing_connections,
                                     key=lambda x: x.reserved_requested_amount,
                                     reverse=True)

        reserved_amount = 0.
        while sorted_reservations:
            max_resources_to_give = (self._amount - reserved_amount) / len(sorted_reservations)
            active_reservation = sorted_reservations.pop()
            active_reservation.reserved_available_amount = min(max_resources_to_give,
                                                               active_reservation.reserved_requested_amount)
            reserved_amount += active_reservation.reserved_available_amount

    def getResource(self, resource_type: str, amount: float) -> float:
        resources_requestable = self.preGetResource(resource_type, amount)
        self._amount -= resources_requestable
        return resources_requestable

    def preGiveResource(self, resource_type: str, amount: float) -> float:
        if resource_type != self._resource_type:
            return 0
        if amount < 0:
            return 0
        if self._max_storage is not None and self._max_storage <= self._amount + amount:
            return self._max_storage - self._amount
        return amount

    def giveResource(self, resource_type: str, amount: float) -> float:
        resources_providable = self.preGiveResource(resource_type, amount)
        self._amount += resources_providable
        if self._resource_type not in self._resources_received_this_tick:
            self._resources_received_this_tick[self._resource_type] = 0
        self._resources_received_this_tick[self._resource_type] += resources_providable
        return resources_providable
