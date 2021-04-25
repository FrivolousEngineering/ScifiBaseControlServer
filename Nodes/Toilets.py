from Nodes.Node import Node
from Nodes.Util import enforcePositive


class Toilets(Node):
    """
    Is more information really needed here? Toilets are as you imagine: They accept water and produce dirty water.
    """
    def __init__(self, node_id: str, **kwargs) -> None:
        super().__init__(node_id, **kwargs)

        self._use_temperature_dependant_effectiveness_factor = False

        # Engineering can't really make the toilets go faster... (well, they could, but not through the engineering
        # console). I don't want to code in "burrito night" to increase the effect of the toilets.
        self._min_performance = 1
        self._max_performance = 1
        self._resources_required_per_tick["water"] = 10
        self._has_settable_performance = False

    def update(self) -> None:
        super().update()

        water_available = self.getResourceAvailableThisTick("water")

        # Technically the toilets could get damaged, but since we won't actually block players from using the toilets
        # when they are broken in game, I'm not going to model that in here.
        dirty_water_left = self._provideResourceToOutgoingConnections("dirty_water", water_available)

        self._resources_produced_this_tick["dirty_water"] = water_available

        dirty_water_provided = enforcePositive(water_available - dirty_water_left)

        self._resources_provided_this_tick["dirty_water"] = dirty_water_provided
