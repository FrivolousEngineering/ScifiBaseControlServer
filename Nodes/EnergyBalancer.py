from Nodes.Node import Node
from Nodes.Util import enforcePositive


class EnergyBalancer(Node):
    """
    The energy balancer is a node that, when connected to two batteries, will ensure that the batteries are mad    """
    def __init__(self, node_id: str, **kwargs) -> None:
        defaults = {}
        defaults.update(kwargs)

        super().__init__(node_id, **defaults)

        self._optional_resources_required_per_tick["energy"] = 10

    def update(self, sub_tick_modifier: float = 1) -> None:
        super().update(sub_tick_modifier)

        energy_available = self.getResourceAvailableThisTick("energy")


        # This node needs a different strategy than "equal spread".
        energy_left = self._provideEnergy(energy_available)

        energy_provided = enforcePositive(energy_available - energy_left)
        self._resources_provided_this_tick["energy"] += energy_provided

    def _provideEnergy(self, amount: float) -> float:
        total_energy_in_connected_nodes = 0

        outgoing_connections = self.getAllOutgoingConnectionsByType("energy")

        for outgoing_connection in outgoing_connections:
            total_energy_in_connected_nodes += outgoing_connection.target.amount_stored

        original_amount = amount
        outgoing_connections = sorted(outgoing_connections,
                                      key=lambda x: x.preGiveResource(amount / len(outgoing_connections)), reverse=True)
        connection_number = 0
        num_connections = len(outgoing_connections)

        for outgoing_connection in outgoing_connections:
            connection_number += 1
            energy_factor = (total_energy_in_connected_nodes - outgoing_connection.target.amount_stored) / total_energy_in_connected_nodes / (num_connections - 1)
            energy_to_provide = energy_factor * original_amount

            energy_dumped = outgoing_connection.giveResource(energy_to_provide)
            amount -= energy_dumped

        return amount

    #TODO: Override addConnection, since this node can *only* be connected with energy storage nodes!