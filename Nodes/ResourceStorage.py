from typing import Optional, Dict, Any

from Nodes.Node import Node
from Nodes.Constants import WEIGHT_PER_UNIT, GAS_PHASE_CHANGE_TEMPERATURE, GAS_PHASE_SPECIFIC_HEAT, SPECIFIC_HEAT
from Nodes.Util import enforcePositive


class ResourceStorage(Node):
    """
    A node that can store a single resource.
    """
    def __init__(self, node_id: str, resource_type: str, amount: float, max_storage: Optional[float] = None, **kwargs) \
            -> None:
        """
        A node that can store a single resource.
        :param node_id: id of this node.
        :param resource_type: The resource that this node stores
        :param amount: How much resources does it have at the moment?
        :param max_storage: How much units of resource can it store
        :param kwargs:
        """
        super().__init__(node_id, **kwargs)
        self._resource_type = resource_type.lower()
        self._amount = amount
        self._max_storage = max_storage
        self._resource_weight_per_unit = WEIGHT_PER_UNIT[self._resource_type]
        self._additional_properties.append("amount_stored")

        self._max_resources_requestable_per_tick = kwargs.get("max_resources_requestable_per_tick", 1000)

        self._description = "This device stores {resource_type}, which can be used by any connected device."
        self._description = self._description.format(resource_type = resource_type)
        self._has_settable_performance = False

    @property
    def max_amount_stored(self) -> float:
        if self._max_storage is None:
            return -1
        return self._max_storage

    def serialize(self) -> Dict[str, Any]:
        data = super().serialize()
        data["amount_stored"] = self._amount
        return data

    def deserialize(self, data: Dict[str, Any]) -> None:
        super().deserialize(data)
        self._amount = data["amount_stored"]

    @property
    def amount_stored(self) -> float:
        return self._amount

    def ensureSaneValues(self) -> None:
        super().ensureSaneValues()

        combined_specific_heat = self._weight * self._specific_heat
        if SPECIFIC_HEAT[self._resource_type] > 0:
            combined_specific_heat += self._amount * SPECIFIC_HEAT[self._resource_type] * self._resource_weight_per_unit
        self._stored_heat = combined_specific_heat * self._temperature

    @property
    def temperature(self):
        resource_specific_heat = SPECIFIC_HEAT[self._resource_type]
        if self._resource_type not in GAS_PHASE_CHANGE_TEMPERATURE:
            return self._stored_heat / (self._weight * self._specific_heat + self._amount * self._resource_weight_per_unit * resource_specific_heat)

        gas_phase_temperature = GAS_PHASE_CHANGE_TEMPERATURE[self._resource_type]

        combined_specific_heat = (self._weight * self._specific_heat) + (self._amount * resource_specific_heat)
        energy_required_to_reach_transition_temp = gas_phase_temperature * combined_specific_heat

        energy_above_gas_transition = self._stored_heat - energy_required_to_reach_transition_temp
        if energy_above_gas_transition < 0:
            # We're below gas transition. Just do whatever the regular is:
            return self._stored_heat / (self._weight * self._specific_heat + self._amount * self._resource_weight_per_unit * resource_specific_heat)

        energy_needed_to_convert_all_into_gas = self._amount * GAS_PHASE_SPECIFIC_HEAT[self._resource_type]

        if energy_needed_to_convert_all_into_gas > energy_above_gas_transition:
            return gas_phase_temperature

        energy_left = energy_above_gas_transition - energy_needed_to_convert_all_into_gas

        return gas_phase_temperature + energy_left / self.weight / self._specific_heat


    @property
    def weight(self) -> float:
        return self._weight + self._resource_weight_per_unit * self.amount_stored

    def preGetResource(self, resource_type: str, amount: float) -> float:
        if resource_type != self._resource_type:
            return 0
        if amount < 0:
            return 0.
        if amount <= self._amount:
            return amount

        return self._amount

    def updateReservations(self) -> None:
        reservations = self.getAllOutgoingConnectionsByType(self._resource_type)
        sorted_reservations = sorted(reservations, key=lambda x: x.reserved_requested_amount, reverse=True)

        reserved_amount = 0.

        while sorted_reservations:
            max_resources_to_give = (min(self._amount, self._max_resources_requestable_per_tick) - reserved_amount) / len(sorted_reservations)
            active_reservation = sorted_reservations.pop()
            active_reservation.reserved_available_amount = min(max_resources_to_give,
                                                               active_reservation.reserved_requested_amount)
            reserved_amount += active_reservation.reserved_available_amount

    def getResource(self, resource_type: str, amount: float) -> float:
        resources_requestable = self.preGetResource(resource_type, amount)
        self._amount -= resources_requestable
        if self._resource_type not in self._resources_provided_this_tick:
            self._resources_provided_this_tick[self._resource_type] = 0.
        self._resources_provided_this_tick[self._resource_type] += resources_requestable
        return resources_requestable

    def preGiveResource(self, resource_type: str, amount: float) -> float:
        if resource_type != self._resource_type:
            return 0.
        if amount < 0:
            return 0.
        if self._max_storage is not None and self._max_storage <= self._amount + amount:
            return enforcePositive(self._max_storage - self._amount)
        return amount

    def giveResource(self, resource_type: str, amount: float) -> float:
        resources_providable = self.preGiveResource(resource_type, amount)
        self._amount += resources_providable
        if self._resource_type not in self._resources_received_this_tick:
            self._resources_received_this_tick[self._resource_type] = 0.
        self._resources_received_this_tick[self._resource_type] += resources_providable
        return resources_providable
