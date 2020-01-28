from Nodes.Node import Node


class ComputationNode(Node):
    """
    A Computation Node is a Node that accepts energy and converts it into data. It is *very* sensitive to heat
    and will break down rapidly if it's not cooled down.

    It has a "use it or lose it" rationale to the data. If no-one consumes the data, it will still consume energy.
    However, it will produce a lot less heat if it's data is not used!
    """

    def __init__(self, node_id: str, **kwargs) -> None:
        super().__init__(node_id, **kwargs)
        self._resources_required_per_tick["energy"] = 10

        self._heat_convection_coefficient = 2  # It's made of plastic or something.
        self._heat_per_data_computed = 100
        self._heat_per_data_not_computed = 20
        self._max_safe_temperature = 353.15  # 80 Degree celcius.

        # It's going to break down pretty darn fast!
        self._temperature_degradation_speed = 3

    def update(self) -> None:
        super().update()

        energy_gained = self.getResourceAvailableThisTick("energy")

        # A Computation node creates 1 energy per energy that it gets. Yay!
        data_available = energy_gained * self.effectiveness_factor

        # Attempt to get rid of the data by offering it to connected sources.
        data_left = self._provideResourceToOutogingConnections("data", data_available)

        # Note that we don't actually store the data we have left over. Data is a "use it or lose it" resource!
        data_produced = max(data_available - data_left, 0)
        self._resources_produced_this_tick["data"] = data_produced

        # But we do give a bit of a discount heat wise!
        heat_produced = data_produced * self._heat_per_data_computed
        heat_produced += data_left * self._heat_per_data_not_computed
        self.addHeat(heat_produced)
