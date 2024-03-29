from Nodes.Node import Node
from Nodes.Util import enforcePositive


class PlantPress(Node):
    """
    The plant press converts plants and energy into food (by squeezing the water out). As such, it also produces a
    tiny bit of water.
    """
    def __init__(self, node_id: str, **kwargs) -> None:
        defaults = {"min_performance": 0.75,
                    "max_performance": 1.5}
        defaults.update(kwargs)
        super().__init__(node_id, **defaults)

        self._resources_required_per_tick["plants"] = 30
        self._resources_required_per_tick["energy"] = 5

        self._water_resevoir = 20

        self._tags.append("mechanical")
        self._tags.append("fuel")

        self._providable_resources.add("food")
        self._providable_resources.add("water")

    def _updateResourceRequiredPerTick(self) -> None:
        """
        If there were resources left over, we should request less resources next time round.
        """
        # max resource that we could produce next tick:
        max_food = min(10 - self._resources_left_over["food"], (self._water_resevoir - self._resources_left_over["water"]) * 2.87)
        max_food = enforcePositive(max_food)
        self._resources_required_per_tick["plants"] = max_food * 3 * self.effectiveness_factor
        self._resources_required_per_tick["energy"] = max_food / 2 * self.effectiveness_factor

    def update(self, sub_tick_modifier: float = 1) -> None:
        super().update(sub_tick_modifier)

        # Get all the resources that we want
        energy_available = self.getResourceAvailableThisTick("energy")
        plants_available = self.getResourceAvailableThisTick("plants")

        self._markResourceAsDestroyed("plants", plants_available)

        # Three plants are needed to create one food. Every 10 foods create 3.5 water, so we need to be able to store
        # 1 water per 2.87 food we produce
        food_produced = min(energy_available * 2, plants_available / 3)

        self._resources_left_over["plants"] = plants_available - food_produced * 3
        self._resources_left_over["energy"] = energy_available - food_produced / 2

        self._markResourceAsCreated("plants", self._resources_left_over["plants"])

        food_produced *= self.effectiveness_factor

        food_left_from_production = self._provideResourceToOutgoingConnections("food", food_produced)
        food_left_from_storage = self._provideResourceToOutgoingConnections("food", self.getResourceAvailableThisTick("food"))

        # Every 10 food units creates 3.5 water
        water_produced = food_produced / 2.87

        self._markResourceAsCreated("water", water_produced)
        self._markResourceAsCreated("food", food_produced)

        water_left_from_production = self._provideResourceToOutgoingConnections("water", water_produced)
        water_left_from_storage = self._provideResourceToOutgoingConnections("water", self.getResourceAvailableThisTick("water"))

        self._resources_left_over["plants"] += food_left_from_production * self.inverted_effectiveness_factor
        self._resources_left_over["energy"] += food_left_from_production * self.inverted_effectiveness_factor
        self._resources_left_over["food"] = food_left_from_production + food_left_from_storage
        self._resources_left_over["water"] = water_left_from_production + water_left_from_storage

        food_provided = enforcePositive(food_produced - food_left_from_production)
        self._resources_provided_this_tick["food"] += food_provided
        self._resources_produced_this_tick["food"] += food_produced

        water_provided = enforcePositive(water_produced - water_left_from_production)
        self._resources_provided_this_tick["water"] += water_provided
        self._resources_produced_this_tick["water"] += water_produced
