from Nodes.Node import Node
from Nodes.Util import enforcePositive


class Toilets(Node):
    """
    Is more information really needed here? Toilets are as you imagine: They accept water and produce dirty water.
    """
    def __init__(self, node_id: str, **kwargs) -> None:
        defaults = {"has_settable_performance": False,
                    "min_performance": 1,
                    "max_performance": 1,
                    "surface_area": 72,
                    "heat_convection_coefficient": 21}
        defaults.update(kwargs)
        super().__init__(node_id, **defaults)

        self._use_temperature_dependant_effectiveness_factor = False

        self._description = "The various sanitary systems located around the base. This system requires clean water " \
                            "to function properly and 'produces' dirty water. Although it's technically possible, " \
                            "it's not recommended to use the dirty water for cooling purposes. Although this will" \
                            "work reasonably well in the normal temperature ranges, it causes blockages when the " \
                            "water starts to evaporate, clogging up the pipes in the process. All factions seem to " \
                            "agree that the effort of cleaning this is simply never worth it"

        # Engineering can't really make the toilets go faster... (well, they could, but not through the engineering
        # console). I don't want to code in "burrito night" to increase the effect of the toilets.
        self._resources_required_per_tick["water"] = 10

        self._providable_resources.add("dirty_water")

    def update(self, sub_tick_modifier: float = 1) -> None:
        original_heat = self._stored_heat
        super().update(sub_tick_modifier)

        water_available = self.getResourceAvailableThisTick("water")
        dirty_water_available = self.getResourceAvailableThisTick("dirty_water")
        # Technically the toilets could get damaged, but since we won't actually block players from using the toilets
        # when they are broken in game, I'm not going to model that in here.

        dirty_water_left = self._provideResourceToOutgoingConnections("dirty_water", water_available + dirty_water_available)
        if original_heat > self._stored_heat:
            # Since dirty_water is heavier than normal water, we need to make sure we don't lose energy (assume that
            # the shit people do adds heat here...)
            self._stored_heat = original_heat

        self._resources_produced_this_tick["dirty_water"] += water_available

        dirty_water_provided = enforcePositive(water_available - dirty_water_left)
        self._resources_left_over["dirty_water"] = dirty_water_left
        self._resources_provided_this_tick["dirty_water"] += dirty_water_provided
