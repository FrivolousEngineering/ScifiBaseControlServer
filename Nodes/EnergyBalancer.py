from typing import cast

from Nodes.Connection import Connection
from Nodes.Node import Node, InvalidConnection
from Nodes.ResourceStorage import ResourceStorage
from Nodes.Util import enforcePositive


class EnergyBalancer(Node):
    """
    The energy balancer is a node that draws a certain amount of power and distributes it in such a way that each
    connected storage gets power depending on how much it has (giving more power if the storage has less).

    This can be used in several setups:
                    ⌜⎺⎺⎺ > B
    A -> Converter -⎟
                    ⌞⎽⎽⎽ > C
    Power is drawn from A and spread to B & C. If B has 0 power and C has 10 power, all power drawn will be moved to B


    Average two batteries
    A <----- Converter <----- B
    ⎟        ^       ⎟        ^
    ⌞ ⎽⎽⎽⎽⎽⎽ ⌟       ⌞ ⎽⎽⎽⎽⎽⎽ ⌟
    Power will first be drawn from both storages and then equally divided.

    """
    def __init__(self, node_id: str, **kwargs) -> None:
        defaults = {}
        defaults.update(kwargs)

        super().__init__(node_id, **defaults)

        self._optional_resources_required_per_tick["energy"] = 10
        self._providable_resources.add("energy")

    def update(self, sub_tick_modifier: float = 1) -> None:
        super().update(sub_tick_modifier)

        energy_available = self.getResourceAvailableThisTick("energy")

        # This node needs a different strategy than "equal spread".
        energy_left = self._provideEnergy(energy_available)

        energy_provided = enforcePositive(energy_available - energy_left)
        self._resources_provided_this_tick["energy"] += energy_provided

    def _provideEnergy(self, amount: float) -> float:
        """
        This node uses a different strategy than equal spread (other nodes distribute evenly)
        :param amount: The amount of energy to distribute
        :return: The amount of energy it couldn't distribute
        """
        total_energy_in_connected_nodes = 0.

        outgoing_connections = self.getAllOutgoingConnectionsByType("energy")

        for outgoing_connection in outgoing_connections:
            # We know the target will be a resource storage, since we don't accept connections that don't
            total_energy_in_connected_nodes += cast(ResourceStorage, outgoing_connection.target).amount_stored

        original_amount = amount
        outgoing_connections = sorted(outgoing_connections,
                                      key=lambda x: x.preGiveResource(amount / len(outgoing_connections)), reverse=True)
        connection_number = 0
        num_connections = len(outgoing_connections)

        for outgoing_connection in outgoing_connections:
            connection_number += 1
            target_node = cast(ResourceStorage, outgoing_connection.target)
            energy_factor = (total_energy_in_connected_nodes - target_node.amount_stored) / total_energy_in_connected_nodes / (num_connections - 1)
            energy_to_provide = energy_factor * original_amount

            energy_dumped = outgoing_connection.giveResource(energy_to_provide)
            amount -= energy_dumped

        return amount

    def ensureConnectionIsPossible(self, connection: Connection) -> None:
        super().ensureConnectionIsPossible(connection)

        if connection.target != self:
            if not isinstance(connection.target, ResourceStorage):
                raise InvalidConnection(f"EnergyBalancer {self._node_id} can only be connected to ResourceStorages")