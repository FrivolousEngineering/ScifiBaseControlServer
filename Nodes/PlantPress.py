from Nodes.Constants import COMBUSTION_HEAT
from Nodes.Node import Node, modifiable_property
from Nodes.Util import enforcePositive


class PlantPress(Node):
    def __init__(self, node_id: str, **kwargs) -> None:
        super().__init__(node_id, **kwargs)

        self._resources_required_per_tick["plants"] = 30
        self._resources_required_per_tick["energy"] = 10

        self._original_resources_required_per_tick = self._resources_required_per_tick.copy()

        self._water_resevoir = 20

        self._tags.append("mechanical")

    def _updateResourceRequiredPerTick(self) -> None:
        # max resource that we could produce next tick:
        max_food = min(10 - self._resources_left_over["food"], (self._water_resevoir - self._resources_left_over["water"]) * 2.87)
        max_food = enforcePositive(max_food)
        self._resources_required_per_tick["plants"] = max_food * 3 * self.effectiveness_factor
        self._resources_required_per_tick["energy"] = max_food * self.effectiveness_factor
        #self._resources_required_per_tick["plants"] = enforcePositive(self._original_resources_required_per_tick["plants"] * self.effectiveness_factor - max_food * 3)

        #self._resources_required_per_tick["energy"] = enforcePositive(self._original_resources_required_per_tick["plants"] * self.effectiveness_factor - max_food)

    def update(self) -> None:
        super().update()

        # Get all the resources that we want
        energy_available = self.getResourceAvailableThisTick("energy")
        plants_available = self.getResourceAvailableThisTick("plants")

        # Three plants are needed to create one food. Every 10 foods create 3.5 water, so we need to be able to store
        # 1 water per 2.87 food we produce
        food_produced = min(energy_available, plants_available / 3)

        self._resources_left_over["plants"] = plants_available - food_produced * 3
        self._resources_left_over["energy"] = energy_available - food_produced
        food_produced *= self.effectiveness_factor

        food_left_from_production = self._provideResourceToOutgoingConnections("food", food_produced)
        food_left_from_storage = self._provideResourceToOutgoingConnections("food", self.getResourceAvailableThisTick("food"))

        # Every 10 food units creates 3.5 water
        water_produced = food_produced / 2.87

        water_left_from_production = self._provideResourceToOutgoingConnections("water", water_produced)
        water_left_from_storage = self._provideResourceToOutgoingConnections("water", self.getResourceAvailableThisTick("water"))

        self._resources_left_over["plants"] += food_left_from_production * self.inverted_effectiveness_factor
        self._resources_left_over["energy"] += food_left_from_production * self.inverted_effectiveness_factor
        self._resources_left_over["food"] = food_left_from_production + food_left_from_storage
        self._resources_left_over["water"] = water_left_from_production + water_left_from_storage

        food_provided = enforcePositive(food_produced - food_left_from_production)
        self._resources_produced_this_tick["food"] = food_provided

        water_provided = enforcePositive(water_produced - water_left_from_production)
        self._resources_produced_this_tick["water"] = water_provided

        # Based on what happened last turn, we should potentially ask for a bit less.
        self._updateResourceRequiredPerTick()
