from Nodes.Node import Node
from Nodes.Util import enforcePositive


class ComputationNode(Node):
    """
    A Computation Node is a Node that accepts energy and converts it into data. It is *very* sensitive to heat
    and will break down rapidly if it's not cooled down.

    It has a "use it or lose it" rationale to the data. If no-one consumes the data, it will still consume energy.
    However, it will produce a lot less heat if it's data is not used!
    """

    def __init__(self, node_id: str, **kwargs) -> None:
        defaults = {"heat_convection_coefficient": 0.51,
                    "temperature_degradation_speed": 30,  # It's going to break down pretty darn fast!
                    "max_safe_temperature": 353.15,  # 80 Degree celcius.
                    "min_performance": 0.25,
                    "max_performance": 4}
        defaults.update(kwargs)

        super().__init__(node_id, **defaults)
        self._resources_required_per_tick["energy"] = 10

        self._heat_per_data_computed = 7000
        self._heat_per_data_not_computed = self._heat_per_data_computed * 0.2

        self._description = "This device requires energy to run, which it requires to generate data. It is *very*" \
                            " sensitive to heat and will break down very rapidly if reaches higher temperatures." \
                            "Even when this device is not generating any data, it will still consume energy and " \
                            "produce heat. The heat production is lower when the data could not be stored."

        self._providable_resources.add("data")
        self._tags.append("electronic")

    def update(self, sub_tick_modifier: float = 1) -> None:
        super().update(sub_tick_modifier)

        energy_gained = self.getResourceAvailableThisTick("energy")
        # A Computation node creates 1 energy per energy that it gets. Yay!
        data_available = energy_gained * self.effectiveness_factor

        # Attempt to get rid of the data by offering it to connected sources.
        data_left = self._provideResourceToOutgoingConnections("data", data_available)

        # Note that we don't actually store the data we have left over. Data is a "use it or lose it" resource!
        data_produced = enforcePositive(data_available - data_left)
        self._resources_produced_this_tick["data"] += data_produced
        self._resources_provided_this_tick["data"] += data_produced

        # But we do give a bit of a discount heat wise!
        heat_produced = data_produced * self._heat_per_data_computed * self.temperature_efficiency
        heat_produced += data_left * self._heat_per_data_not_computed
        self.addHeat(heat_produced)
