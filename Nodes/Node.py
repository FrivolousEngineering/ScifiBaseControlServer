from threading import RLock
from typing import List, Dict, Any, Set

from collections import defaultdict
from Nodes.Connection import Connection
from Nodes.Constants import SPECIFIC_HEAT, WEIGHT_PER_UNIT
from Nodes.Modifiers.Modifier import Modifier
from Nodes.Modifiers.ModifierFactory import ModifierFactory
from Signal import signalemitter, Signal

from functools import wraps


class InvalidConnection(Exception):
    pass


def modifiable_property(f):
    """
    A modifiable property is one that can be modified by, you guessed it, modifiers.

    If a property has a max_{property_name}, it will also be used to clamp it's max.
    :param f:
    :return:
    """

    @wraps(f)
    def wrapper(self, *args, **kwargs):
        modifier_value = 0
        factor_value = 1.0
        property_name = f.__name__
        for modifier in self._modifiers:
            modifier_value += modifier.getModifierForProperty(property_name)
            factor_value *= modifier.getFactorForProperty(property_name)

        unmodified_value = f(self, *args, **kwargs)
        final_value = factor_value * unmodified_value + modifier_value
        try:
            return min(getattr(self, "max_" + property_name), final_value)
        except AttributeError:
            return final_value
    return property(wrapper)


resource_dict = Dict[str, float]


@signalemitter
class Node:
    """
    This is an abstract class. Most objects in the system should inherit from this base class.
    Nodes itself can be connected by Connections to move resources around.
    Nodes can produce and require a certain amount of resources per tick.
    """

    outside_temp = 293.15

    preUpdateCalled = Signal()
    updateCalled = Signal()
    postUpdateCalled = Signal()

    _description: str = ""
    """Description for this type of node"""

    def __init__(self, node_id: str, temperature: float = 293.15, **kwargs) -> None:
        """
        :param node_id: Unique identifier of the node.
        :param temperature: The starting temperature of the node
        """
        self._node_id = node_id
        self._incoming_connections = []  # type: List[Connection]
        self._outgoing_connections = []  # type: List[Connection]

        self._resources_required_per_tick: resource_dict = {}
        """ What resources must this node get in order to function? """

        self._original_resources_required_per_tick: resource_dict = {}
        """Resources required per tick holds the current (modified) amount. This holds the unmodified amounts"""

        self._optional_resources_required_per_tick: resource_dict = {}
        """What resources does this node want in order to function, but it could do without?"""
        self._original_optional_resources_required_per_tick: resource_dict = {}
        self._optional_resources_required_last_tick: resource_dict = {}

        self._resources_received_this_tick: resource_dict = defaultdict(float)
        self._resources_produced_this_tick: resource_dict = defaultdict(float)
        self._resources_provided_this_tick: resource_dict = defaultdict(float)

        self._resources_received_this_sub_tick: resource_dict = defaultdict(float)

        self._resources_required_last_tick: Dict[str, float] = {}
        self._resources_received_last_tick: resource_dict = {}
        self._resources_produced_last_tick: resource_dict = {}
        self._resources_provided_last_tick: resource_dict = {}

        self._resources_left_over: resource_dict = defaultdict(float)
        """Any resources that were left from previous (ticks) that could not be left anywhere."""

        self._weight: float = kwargs.get("weight", 300)

        self._specific_heat: float = 420
        """ How much energy is needed to increase 1kg of this node by one degree"""

        self._stored_heat: float = self._weight * temperature * self._specific_heat
        """How much heat is stored inside this object. This is used to calculate the energy"""

        self._temperature: float = temperature
        """Temperature is in kelvin"""

        self._heat_emissivity: float = kwargs.get("heat_emissivity", 0.5)
        """How well does this node emit heat. 0 is a perfect reflector, 1 is the sun."""

        self._enabled: bool = kwargs.get("enabled", True)
        """Is the node working at all?"""

        self._can_be_modified: bool = kwargs.get("can_be_modified", True)
        """Can this node receive modifiers?"""

        self._update_lock = RLock()

        # A few examples of heat_convection_coefficient all in W/m K:
        # Plastic: 0.1-0.22
        # Stainless steel: 16-24
        # Aluminum: 205 - 250
        self._heat_convection_coefficient: float = kwargs.get("heat_convection_coefficient", 10.)

        self._surface_area: float = kwargs.get("surface_area", 1)
        """How large is the surface of this object (in M2)"""

        self.__stefan_boltzmann_constant: float = 5.67e-8
        """A constant for heat."""

        self._additional_properties: List[str] = ["health"]

        self._health: float = kwargs.get("health", 100.)
        self._max_health: float = 100.
        self._active: bool = False
        self._max_safe_temperature: float = kwargs.get("max_safe_temperature", 400)

        self._performance: float = kwargs.get("performance", 1.)
        """At what level should this node perform? Factor that runs from 0 to x, where 1 is normal performance"""

        self._target_performance: float = kwargs.get("target_performance", 1.)

        self._min_performance: float = kwargs.get("min_performance", 1)
        self._max_performance: float = kwargs.get("max_performance", 1)

        self._has_settable_performance: bool = kwargs.get("has_settable_performance", True)

        self._usage_damage_factor: float = kwargs.get("usage_damage_factor", 0.)
        """How much damage should this node get by being in use?"""

        self._temperature_degradation_speed: float = kwargs.get("temperature_degradation_speed", 1)
        """How fast should this node degrade if it's above a certain temperature?"""

        self._custom_description = kwargs.get("custom_description", "")  # type: str
        """Description specific to this node"""

        self._label = kwargs.get("label", "")
        """Human readable name for this Node"""

        self._modifiers = []  # type: List[Modifier]

        self._use_temperature_dependant_effectiveness_factor = False

        # Does this node change it's performance instantly?
        # a value of 1 means it changes instantly, higher values means it changes slower.
        self._performance_change_factor: float = kwargs.get("performance_change_factor", 2)

        self._optimal_temperature: float = kwargs.get("optimal_temperature", 375)
        self._optimal_temperature_range: float = kwargs.get("optimal_temperature_range", 75)

        self._temperature_efficiency: float = kwargs.get("temperature_efficiency", 1)
        """How (in)efficient is the Node. This is only for nodes that produce something and heat at the same time.
        An efficiency of 0 means that no heat is produced. An efficiency of 1 means that all heat of production is
        transformed into heat. Note that this does not have an effect on the actual resources produced, just the heat"""

        self._tags: List[str] = []

        self._seconds_per_tick = 60

        self._acceptable_resources: Set[str] = set()
        self._providable_resources: Set[str] = set()

        self._logistics_factor = 1.
        """
        If there are resources that it was unable to provide, it might be that the node needs to request less resources
        next time round. This factor handles that.
        """
        self._optional_logistics_factor = 1.

    @property
    def combined_specific_heat(self) -> float:
        total_specific_heat = self._weight * self._specific_heat

        for resource_type, amount in self._resources_left_over.items():
            total_specific_heat += SPECIFIC_HEAT[resource_type] * amount * WEIGHT_PER_UNIT[resource_type]

        return total_specific_heat

    @property
    def additional_properties(self):
        """
        A list of additional properties that can be retrieved (for example, the ResourceStorage has "amount")
        This is to notify the other observers that the property exists (for example, the NodeHistory uses this).
        If the max value a property can take should also be communicated, the max_{property_name} is also requested
        :return:
        """
        return self._additional_properties

    @property
    def tags(self) -> List[str]:
        """
        Tags can be used to label a node as being of a specific type.
        Consider options like "mechanical", "electronic", etc.
        Certain modifiers require a certain tag to be present before they can be set on a node.
        """
        return self._tags

    @property
    def hasSettablePerformance(self):
        return self._has_settable_performance

    @property
    def isTemperatureDependant(self):
        return self._use_temperature_dependant_effectiveness_factor

    def ensureSaneValues(self) -> None:
        """
        This is to ensure that when custom performance is set that any updates are done.
        Due to child classes changing how this behavior can be, it's hard to get it in the constructor.
        As such we just let an external class ensure this bit of bookkeeping is done.
        """
        self._original_resources_required_per_tick = self._resources_required_per_tick.copy()
        self._original_optional_resources_required_per_tick = self._optional_resources_required_per_tick.copy()
        self._resources_required_last_tick = self._resources_required_per_tick.copy()
        self._optional_resources_required_last_tick = self._optional_resources_required_per_tick.copy()
        self._setPerformance(self.performance)

        self._stored_heat = self.weight * self._specific_heat * self._temperature
        self._acceptable_resources.update(self._resources_required_per_tick.keys())
        self._acceptable_resources.update(self._optional_resources_required_per_tick.keys())

    @modifiable_property
    def temperature_efficiency(self):
        return self._temperature_efficiency

    @modifiable_property
    def temperature_degradation_speed(self):
        return self._temperature_degradation_speed

    @modifiable_property
    def optimal_temperature(self):
        return self._optimal_temperature

    @modifiable_property
    def optimal_temperature_range(self):
        return self._optimal_temperature_range

    @modifiable_property
    def usage_damage_factor(self):
        return self._usage_damage_factor

    @property
    def can_be_modified(self) -> bool:
        return self._can_be_modified

    @property
    def label(self) -> str:
        if self._label:
            return self._label
        return self._node_id

    def getModifiers(self) -> List[Modifier]:
        """
        Get all the modifiers on this node.
        :return: List of modifiers
        """
        return self._modifiers

    def addModifier(self, modifier: Modifier) -> None:
        """
        Add a Modifier to the node. Modifiers can be used to (temporarily) change behaviors / stats of a node
        :param modifier:  The modifier to add
        """
        if not self._can_be_modified:
            return

        existing_modifier = None
        for mod in self._modifiers:
            if mod.name == modifier.name:
                existing_modifier = mod
                break

        if existing_modifier:
            self._modifiers.remove(existing_modifier)

        self._modifiers.append(modifier)
        modifier.setNode(self)

    def _markResourceAsDestroyed(self, resource_type: str, amount: float) -> None:
        """
        If a resource is used up somehow, the node still got extra energy for receiving it in the first place!
        If it were to just disappear, this would cause the node to heat up (it got the energy, but the mass is suddenly
        gone!). This function makes sure that the heat bookkeeping is updated.

        Yes; This breaks all kinds of physics rules. But its a big hassle to ensure that all the inputs & outputs
        of each node are 100% correct
        :param resource_type:
        :param amount:
        :return:
        """
        energy_lost = amount * self.temperature * SPECIFIC_HEAT[resource_type] * WEIGHT_PER_UNIT[resource_type]
        self.addHeat(-energy_lost)

    def _markResourceAsCreated(self, resource_type:str, amount:float) -> None:
        """
        If a resource is created, extra energy needs to be added.

        Yes; This breaks all kinds of physics rules. But its a big hassle to ensure that all the inputs & outputs
        of each node are 100% correct
        :param resource_type:
        :param amount:
        :return:
        """
        energy_added = amount * self.temperature * SPECIFIC_HEAT[resource_type] * WEIGHT_PER_UNIT[resource_type]
        self.addHeat(energy_added)

    def removeModifier(self, modifier: Modifier) -> None:
        """
        Remove a modifier from the node. If it's not found, nothing happens.
        :param modifier: The modifier to remove.
        """
        try:
            self._modifiers.remove(modifier)
        except ValueError:
            pass

    @modifiable_property
    def min_performance(self):
        return self._min_performance

    @modifiable_property
    def max_performance(self):
        return self._max_performance

    @modifiable_property
    def performance(self) -> float:
        return self._performance

    def _setPerformance(self, new_performance: float) -> None:
        """
        Set the performance of a node and do a bunch of bookkeeping to make sure that the resources it wants next tick
        is updated
        :param new_performance: New performance to be used
        """
        with self._update_lock:
            self._performance = new_performance
            for resource in self._resources_required_per_tick:
                if resource not in self._original_resources_required_per_tick:
                    self._original_resources_required_per_tick[resource] = self._resources_required_per_tick[resource]
                self._resources_required_per_tick[resource] = self._original_resources_required_per_tick[
                                                                  resource] * self._performance * self._logistics_factor

            for resource in self._optional_resources_required_per_tick:
                if resource not in self._original_optional_resources_required_per_tick:
                    self._original_optional_resources_required_per_tick[resource] = self._optional_resources_required_per_tick[resource]

                self._optional_resources_required_per_tick[resource] = self._original_optional_resources_required_per_tick[
                                                                  resource] * self._performance * self._optional_logistics_factor

    @property
    def target_performance(self) -> float:
        return self._target_performance

    @target_performance.setter
    def target_performance(self, new_performance: float) -> None:
        with self._update_lock:
            self._target_performance = new_performance
            if self._target_performance < self.min_performance:
                self._target_performance = self.min_performance
            elif self._target_performance > self.max_performance:
                self._target_performance = self.max_performance

            if self._performance_change_factor == 1:
                self._setPerformance(self._target_performance)

    @modifiable_property
    def heat_emissivity(self) -> float:
        return self._heat_emissivity

    @property
    def surface_area(self) -> float:
        return self._surface_area

    @modifiable_property
    def heat_convection_coefficient(self) -> float:
        return self._heat_convection_coefficient

    @modifiable_property
    def max_safe_temperature(self) -> float:
        return self._max_safe_temperature

    @property
    def description(self) -> str:
        return self._description

    @property
    def custom_description(self) -> str:
        return self._custom_description

    @modifiable_property
    def health(self) -> float:
        return min(self.max_health, self._health)

    @property
    def max_health(self) -> float:
        return self._max_health

    def repair(self, amount: float) -> None:
        """
        Repair the node
        :param amount: Amount to repair
        """
        if amount < 0.:
            amount = 0.
        self._health += amount
        if self._health > self.max_health:
            self._health = self.max_health

    def damage(self, amount: float) -> None:
        """
        Deal a certain amount of damage to this node.
        :param amount: Amount of damage to deal
        """
        self._health -= amount
        if self._health < 0:
            self._health = 0

    def _updateResourceRequiredPerTick(self) -> None:
        """
        Depending on what happend the last update, it might be needed to update the required resources for the next
        tick.
        :return:
        """
        pass

    @property
    def enabled(self) -> bool:
        return self._enabled

    @enabled.setter
    def enabled(self, enabled: bool) -> None:
        with self._update_lock:
            self._enabled = enabled

    @property
    def active(self):
        return self._active

    def acquireUpdateLock(self) -> None:
        """
        When an update is active, requests for info should wait until the update is done. This ensure that.
        .. seealso:: :meth:`Nodes.Node.Node.releaseUpdateLock` on how to release the lock
        """
        self._update_lock.acquire()

    def releaseUpdateLock(self) -> None:
        """
        Release the update lock.

        .. seealso:: :meth:`Nodes.Node.Node.acquireUpdateLock` on how to acquire a lock

        """
        try:
            self._update_lock.release()
        except RuntimeError:
            pass  # We don't care about releasing an unlocked lock

    def serialize(self) -> Dict[str, Any]:
        """
        Serialize this node so that it can be stored somewhere (eg; save to file)
        :return: A dict with keys for the attribute.
        """
        result = dict()  # type: Dict[str, Any]
        result["node_id"] = self._node_id
        result["label"] = self._label
        result["resources_received_this_tick"] = self._resources_received_this_tick
        result["resources_produced_this_tick"] = self._resources_produced_this_tick
        result["resources_provided_this_tick"] = self._resources_provided_this_tick
        result["resources_provided_last_tick"] = self._resources_provided_last_tick
        result["resources_required_per_tick"] = self._resources_required_per_tick
        result["optional_resources_required_per_tick"] = self._optional_resources_required_per_tick
        result["optional_resources_required_last_tick"] = self._optional_resources_required_last_tick
        result["original_optional_resources_required_per_tick"] = self._original_optional_resources_required_per_tick
        result["resources_required_last_tick"] = self._resources_required_last_tick

        result["resources_produced_last_tick"] = self._resources_produced_last_tick
        result["resources_received_last_tick"] = self._resources_received_last_tick

        result["resources_left_over"] = self._resources_left_over
        result["health"] = self._health
        result["stored_heat"] = self._stored_heat
        result["performance"] = self._performance
        result["target_performance"] = self._target_performance
        result["active"] = self._active
        result["modifiers"] = []

        for modifier in self._modifiers:
            result["modifiers"].append(modifier.serialize())

        return result

    def deserialize(self, data: Dict[str, Any]) -> None:
        """
        Restore the data of a node from serialized information. (eg: load from file)
        :param data:
        """
        self._node_id = data["node_id"]
        self._label = data.get("label")
        self._resources_received_this_tick.update(data["resources_received_this_tick"])
        self._resources_produced_this_tick.update(data["resources_produced_this_tick"])
        self._resources_provided_this_tick.update(data["resources_provided_this_tick"])
        self._resources_provided_last_tick.update(data["resources_provided_last_tick"])
        self._resources_produced_last_tick.update(data["resources_produced_last_tick"])
        self._optional_resources_required_last_tick.update(data["optional_resources_required_last_tick"])
        self._resources_required_last_tick.update(data["resources_required_last_tick"])

        self._optional_resources_required_per_tick.update(data["optional_resources_required_per_tick"])
        self._resources_required_per_tick.update(data["resources_required_per_tick"])
        self._resources_received_last_tick.update(data["resources_received_last_tick"])

        self._original_optional_resources_required_per_tick.update(data["original_optional_resources_required_per_tick"])

        self._resources_left_over = data["resources_left_over"]

        self._stored_heat = data["stored_heat"]
        self._health = data.get("health", 100)
        self._performance = data["performance"]

        self._target_performance = data.get("target_performance", 1.)
        if self._target_performance < self.min_performance:
            self._target_performance = self.min_performance
        elif self._target_performance > self.max_performance:
            self._target_performance = self.max_performance

        self._active = data["active"]

        for modifier in data.get("modifiers", []):
            mod = ModifierFactory.createModifier(modifier["type"])
            if mod:
                mod.deserialize(modifier)
                self.addModifier(mod)
        self._recalculateTemperature()

    @property
    def weight(self):
        extra_weight = 0
        for resource, amount in self._resources_left_over.items():
            extra_weight += WEIGHT_PER_UNIT[resource] * amount
        return self._weight + extra_weight

    @modifiable_property
    def performance_change_factor(self):
        return self._performance_change_factor

    @modifiable_property
    def temperature(self):
        """
        The temperature of this node in Kelvin
        """
        return self._temperature

    def _recalculateTemperature(self) -> None:
        """
        Update the temperature of this node. This isn't done every time the temperature is requested to prevent
        issues with nodes that pass through resources.
        :return:
        """
        self._temperature = self._stored_heat / self.combined_specific_heat

    def addHeat(self, heat_to_add: float) -> None:
        """
        Add an amount of heat to this node. Can be negative or positive.
        :param heat_to_add: The amount of heat to add (or subtract)
        """
        self._stored_heat += heat_to_add

    def __repr__(self):
        return f"Node ('{self._node_id}', a {type(self).__name__})"

    def updateReservations(self) -> None:
        """
        Update the reservations of a node. By default, this does nothing. It's up to sublcasses to implement
        """
        pass

    def getId(self) -> str:
        """
        Get unique identifier of this node.
        :return: The unique ID
        """
        return self._node_id

    def getResourcesRequiredPerTick(self) -> Dict[str, float]:
        """
        Get all the resources that are required this tick. Note that this doesn't contain optional requirements!
        :return:
        """
        return self._resources_required_per_tick

    def getResourcesRequiredLastTick(self) -> Dict[str, float]:
        """
        Get all the resources that are required last tick. Note that this doesn't contain optional requirements!
        This can be used to display information since this is the most up to date info that there is
        :return:
        """
        return self._resources_required_last_tick

    def getResourcesRequiredPreviousTick(self):
        """
        Get all the resources that are required previous tick. Note that this doesn't contain optional requirements!
        This can be used to display information since this is the most up to date info that there is
        :return:
        """
        return self._resources_required_last_tick

    def getAllResourcesRequiredPerTick(self) -> Dict[str, float]:
        """
        Get all the resources that are required this tick, including the optional ones!
        :return:
        """
        result = self._resources_required_per_tick.copy()

        for resource, value in self._optional_resources_required_per_tick.items():
            if resource not in result:
                result[resource] = value
            else:
                result[resource] += value
        return result

    def getOptionalResourcesRequiredLastTick(self) -> Dict[str, float]:
        """
        Get the list of optional resources that this node needed last tick. This can be used to display information
        what the node 'currently' needs (since this is the most up to date info that there is).
        :return:
        """
        return self._optional_resources_required_last_tick

    def getResourcesReceivedThisTick(self) -> Dict[str, float]:
        """
        How much resources did this node get this tick?
        :return:
        """
        return self._resources_received_this_tick

    def getResourcesReceivedLastTick(self) -> Dict[str, float]:
        """
        How much resources did this node get last tick?  This can be used to display information
        what the node 'currently' received (since this is the most up to date info that there is).
        :return:
        """
        return self._resources_received_last_tick

    def getResourcesProducedThisTick(self) -> Dict[str, float]:
        """
        How much resources did this node produce this tick. Note that this is not the same as how much it actually
        provided other nodes!
        :return:
        """
        return self._resources_produced_this_tick

    def getResourcesProducedLastTick(self) -> Dict[str, float]:
        """
        How much resources did this node produce last tick. Note that this is not the same as how much it actually
        provided other nodes!  This can be used to display information, since this is the most up to date info.
        :return:
        """
        return self._resources_produced_last_tick

    def getResourcesProvidedThisTick(self) -> Dict[str, float]:
        """
        How much resources did this node provide this tick. Note that this is not the same as how much it actually
        produced! It can provide *more* resources than it produced if it had something left from previous updates.
        :return:
        """
        return self._resources_provided_this_tick

    def getResourcesProvidedLastTick(self) -> Dict[str, float]:
        """
        How much resources did this node provide this tick. Note that this is not the same as how much it actually
        produced! It can provide *more* resources than it produced if it had something left from previous updates.
        This can be used to display information, since this is the most up to date info.
        :return:
        """
        return self._resources_provided_last_tick

    def getResourceAvailableThisTick(self, resource_type: str) -> float:
        """
        Convenience function that combines the resources that this node got this tick and whatever was left over.
        It can happen that resources were requested in a previous tick, that could not be used (because of various
        reasons).
        Since it's super annoying to give those back, the node will just keep them in storage (and try to re-use them
        in the next tick.

        :param resource_type: Type of the resource to check for
        :return: Amount of resources of the given type that can be used this tick.
        """
        return self._resources_received_this_sub_tick.get(resource_type.lower(), 0.) + self._resources_left_over.get(resource_type.lower(), 0.)
        #return self._resources_received_this_tick.get(resource_type.lower(), 0.) + self._resources_left_over.get(
        #    resource_type.lower(), 0.)

    def preUpdate(self) -> None:
        """
        Ensure that everything is set up so that the actual work can be done. This includes ensuring that the
        correct resource reservations are made
        """
        self.preUpdateCalled.emit(self)

        self._updatePerformance()
        all_resources = self.getAllResourcesRequiredPerTick()
        for resource_type in all_resources:
            connections = self.getAllIncomingConnectionsByType(resource_type)
            if not connections:
                # Can't get the resource at all!
                continue
            total_resource_to_reserve = all_resources[resource_type] \
                                        - self._resources_left_over.get(resource_type, 0)
            resource_to_reserve = total_resource_to_reserve / len(connections)

            for connection in connections:
                connection.reserveResource(resource_to_reserve)

    def _updatePerformance(self) -> None:
        """
        Since we have a target performance and an actual performance, this function needs to be regulary called to
        make sure that the actual performance moves toward the target performance
        """
        # Performance works with a target and an actual performance.
        if self.performance == self.target_performance:
            return

        new_performance = self.performance + (self.target_performance - self.performance) / max(self.performance_change_factor, 1)

        if abs(new_performance - self.target_performance) < 0.001:
            new_performance = self.target_performance

        self._setPerformance(new_performance)

    def _getReservedResourceByType(self, resource_type: str, sub_tick_modifier: float) -> float:
        """
        Get a given resource, provided it was reserved, from all connections that can give it.
        :param resource_type: The type of the resource to get
        :param sub_tick_modifier: Number between 0 and 1. One being a "full" tick, and 0.1 being 1/10th of a tick.
        :return: Amount of the resource obtained
        """
        result = 0.
        for connection in self.getAllIncomingConnectionsByType(resource_type):
            result += connection.getReservedResource(sub_tick_modifier)
        return result

    def _provideResourceToOutgoingConnections(self, resource_type: str, amount: float) -> float:
        """
        Provide resources of a given type to all outgoing connections. It's possible that not all resources could be
        moved. In this case the return value is > 0 (indicating how much could not be moved to another node).

        :param resource_type: Type of resource to move to connected nodes
        :param amount: How much of the resource needs to be moved?
        :return: How much resource was left after attempting to move it.
        """
        outgoing_connections = self.getAllOutgoingConnectionsByType(resource_type)
        outgoing_connections = sorted(outgoing_connections,
                                      key=lambda x: x.preGiveResource(amount / len(outgoing_connections)),
                                      reverse=True)
        while outgoing_connections:
            active_connection = outgoing_connections.pop()
            resources_stored = active_connection.giveResource(amount / (len(outgoing_connections) + 1))
            amount -= resources_stored
        return amount

    def _getAllReservedResources(self, sub_tick_modifier: float) -> None:
        """
        Once the planning is done, this function ensures that all reservations actually get executed.
        The results are places in the _resources_received_this_tick dict.
        :param sub_tick_modifier: Number between 0 and 1. One being a "full" tick, and 0.1 being 1/10th of a tick.
        """
        all_resources = self.getAllResourcesRequiredPerTick()
        for resource_type in all_resources:
            already_received_resources = self._resources_received_this_sub_tick.get(resource_type, 0)
            reserved_resources = self._getReservedResourceByType(resource_type, sub_tick_modifier)
            self._resources_received_this_sub_tick[resource_type] = reserved_resources + already_received_resources
            if resource_type not in self._resources_received_this_tick:
                self._resources_received_this_tick[resource_type] = 0

            self._resources_received_this_tick[resource_type] += reserved_resources + already_received_resources

    def replanReservations(self) -> None:
        """
        If for whatever reason the initial reservations can not be met, this function will attempt to ask more of the
        connections that did fulfill what was asked for (hoping that those can provide more resources)
        """
        all_resources = self.getAllResourcesRequiredPerTick()
        for resource_type in all_resources:
            connections = self.getAllIncomingConnectionsByType(resource_type)
            total_resource_deficiency = sum([connection.getReservationDeficiency() for connection in connections])
            num_satisfied_reservations = len(
                [connection for connection in connections if connection.isReservationSatisfied()])

            if num_satisfied_reservations == 0:
                extra_resource_to_ask_per_connection = 0.
            else:
                extra_resource_to_ask_per_connection = total_resource_deficiency / num_satisfied_reservations
            for connection in connections:
                if not connection.isReservationSatisfied():
                    # So the connection that could not meet demand needs to be locked (since we can't get more!)
                    connection.lock()
                else:
                    if extra_resource_to_ask_per_connection == 0:
                        connection.lock()
                        continue
                    # So the connections that did give us that we want might have a bit more!
                    connection.reserveResource(
                        connection.reserved_requested_amount + extra_resource_to_ask_per_connection)

    def update(self, sub_tick_modifier: float = 1) -> None:
        """
        Do the actual update for this node. Use sub_tick_modifier for "micro" updates
        :param sub_tick_modifier:  Number between 0 and 1. One being a "full" tick, and 0.1 being 1/10th of a tick.
        """
        self.updateCalled.emit(self)
        self._getAllReservedResources(sub_tick_modifier)

    def _reEvaluateIsActive(self) -> bool:
        """
        Reevaluate if this node should be considered to be active.
        This is done by checking if it received all the resources it needed to do it's thing.
        :return: True if it's active, false otherwise.
        """
        for resource_required, amount_needed in self._resources_required_per_tick.items():
            # Do a fuzzy match, as it can sometimes happen that it gets 0.99999999 if it asks for 1.
            if self._resources_received_this_tick.get(resource_required, 0) < amount_needed * 0.99:
                return False
        return True

    def postUpdate(self) -> None:
        """
        Cleanup after all the updating is done. This mostly does a bunch of bookkeeping (damage, heat, etc)
        """
        self._updateResourceRequiredPerTick()
        self._active = self._reEvaluateIsActive()
        self._emitHeat()
        self._convectiveHeatTransfer()
        self._recalculateTemperature()
        self._dealDamageFromHeat()
        self._dealDamageFromUsage()
        self._resources_required_last_tick = self._resources_required_per_tick.copy()
        self._resources_received_last_tick = self._resources_received_this_tick.copy()
        self._optional_resources_required_last_tick = self._optional_resources_required_per_tick.copy()
        self._resources_produced_last_tick = self._resources_produced_this_tick.copy()
        self._resources_provided_last_tick = self._resources_provided_this_tick.copy()

        self.postUpdateCalled.emit(self)
        for connection in self._outgoing_connections:
            connection.reset()
        self._resources_received_this_tick.clear()
        self._resources_received_this_sub_tick.clear()
        self._resources_produced_this_tick.clear()
        self._resources_provided_this_tick.clear()

    def updateModifiers(self) -> None:
        """
        Update the timers of the modifiers (and remove them if they have expired)
        """
        for modifier in self._modifiers:
            modifier.update()

    def cleanupAfterUpdate(self) -> None:
        """
        Due to the sub ticks, this needs to be done after every update (whereas postUpdate is only done after all
        updates are done)
        :return:
        """
        self._resources_received_this_sub_tick.clear()
        self._recalculateTemperature()

    def _emitHeat(self) -> None:
        """
        Heat also leaves objects by grace of radiation. This is calculated by the The Stefan-Boltzmann Law
        """
        temp_diff = pow(self.outside_temp, 4) - pow(self.temperature, 4)
        heat_radiation = self.__stefan_boltzmann_constant * self.heat_emissivity * self._surface_area * temp_diff
        self.addHeat(heat_radiation * self._seconds_per_tick)

        if heat_radiation < 0:
            if self.temperature < self.outside_temp:
                # We were warmer than the outside before, but no amount of radiation can make us go lower!
                self._temperature = self.outside_temp

    def _convectiveHeatTransfer(self) -> None:
        """
        Handle the convective heat transfer.
        This uses a simplified formula, which depends on surface area, temp difference and heat_convection_coefficient
        """
        delta_temp = self.outside_temp - self.temperature
        heat_convection = self.heat_convection_coefficient * self._surface_area * delta_temp
        self.addHeat(heat_convection * self._seconds_per_tick)
        if heat_convection < 0:  # Cooling down happened.
            if self.temperature < self.outside_temp:
                # We were warmer than the outside before, but no amount of convection can make us go lower!
                self._temperature = self.outside_temp

    def _dealDamageFromHeat(self) -> None:
        """
        If nodes get too hot (above the max safe temperature) they are damaged
        """
        delta_temp = self.temperature - self._max_safe_temperature
        if delta_temp <= 0:
            return
        self.damage(self.temperature_degradation_speed * (delta_temp / self._max_safe_temperature))

    def _dealDamageFromUsage(self) -> None:
        """
        If a node was active, check if damage needs to be done because of wear & tear.
        :return:
        """
        if self._active and self.usage_damage_factor > 0:
            self.damage(self.usage_damage_factor * self.performance)

    def _getHealthEffectivenessFactor(self) -> float:
        """
        Calculate how much efficiency is left due to the heath of this node.
        :return: The factor (between 0 and 1)
        """

        health_factor = self._health / self.max_health
        # This makes the effectiveness a bit less punishing.
        # 75% health: 90% effectiveness
        # 50% health: 75% effectiveness
        # 25% health: 50% effectiveness
        # 10% health: 25% effectiveness
        # 1%  health: ~3% effectiveness
        factor = 0.75 * (2 - 1 / (health_factor + 0.5))

        if factor < 0:
            factor = 0

        if factor > 1:
            factor = 1
        return factor

    @property
    def health_effectiveness_factor(self) -> float:
        """
        If the node doesn't have a temperature dependant efficiency, will be the same as effectiveness_factor
        The main reason you would want to use this instead of the effectiveness factor, is when you only want to take
        the health into account (eg; A generator will not produce energy as fast, but it did burn all the fuel). As such
        only the health should be taken into account!
        :return:
        """
        return self._getHealthEffectivenessFactor()

    @property
    def inverted_health_effectiveness_factor(self) -> float:
        try:
            return 1 / self.health_effectiveness_factor
        except ZeroDivisionError:
            return 1

    @property
    def effectiveness_factor(self) -> float:
        factor = self._getHealthEffectivenessFactor()

        if not self._use_temperature_dependant_effectiveness_factor:
            return factor

        # Now to compensate a bit for temperature
        temperature_difference = abs(self.temperature - self.optimal_temperature)
        temperature_difference = min(self.optimal_temperature_range, temperature_difference)

        # This factor runs from 0 to 1
        t = 1. - (temperature_difference / self.optimal_temperature_range)

        # Add a nice easing function.
        if t < 0.5:
            result = 4 * t * t * t
        else:
            p = 2 * t - 2
            result = 0.5 * p * p * p + 1
        return factor * result

    @property
    def inverted_effectiveness_factor(self) -> float:
        try:
            return 1 / self.effectiveness_factor
        except ZeroDivisionError:
            return 1

    def requiresReplanning(self) -> bool:
        """
        Does this node need another replan step in order to get more resources.
        Do keep in mind that even if this returns false, it does not mean that it got everything that it asked for (just
        that nothing more can be done to ensure that it happens). If a node did get everything it asked, no replanning
        is needed.

        :return: If a replan is needed or not
        """
        if not self.enabled:
            return False  # Disabled nodes don't need replanning!
        num_satisfied_reservations = len(
            [connection for connection in self._incoming_connections if connection.isReservationSatisfied()])

        if not num_satisfied_reservations:
            return False
        return len(self._incoming_connections) != num_satisfied_reservations

    def ensureConnectionIsPossible(self, connection: Connection) -> None:
        """
        Check if a given connection that is being made is possible at all. If it's invalid, an InvalidConnection is
        raised.
        :param connection:
        :return:
        """
        if connection.target == self:
            if connection.resource_type not in self._acceptable_resources:
                raise InvalidConnection(f"Node [{self._node_id}] is unable to accept resources of type {connection.resource_type}")
        else:
            if connection.resource_type not in self._providable_resources:
                raise InvalidConnection(
                    f"{type(self).__name__} with ID [{self._node_id}] is unable to provide resources of type {connection.resource_type}")

    def connectWith(self, resource_type: str, target: "Node") -> None:
        """
        Create a connection that transports the provided resource_type from this node to the provided node.
        :param resource_type: The resource that this node needs to connect.
        :param target: The node that is the target of the connection
        :return:
        """
        with self._update_lock:
            new_connection = Connection(origin=self, target=target, resource_type = resource_type)
            self._outgoing_connections.append(new_connection)
            target.addConnection(new_connection)

    def addConnection(self, connection: Connection) -> None:
        """
        Add a connection to this Node.
        :param connection: The connection to add
        :return:
        """
        with self._update_lock:
            self._incoming_connections.append(connection)

    def getAllOutgoingConnections(self) -> List[Connection]:
        """
        Get all the connections that the node can move resources from itself to somewhere else
        :return: The list of connections
        """
        return self._outgoing_connections

    def getAllIncomingConnections(self) -> List[Connection]:
        """
        Get all the connections that can provide resources to this node
        :return: The list of connections
        """
        return self._incoming_connections

    def getAllIncomingConnectionsByType(self, resource_type: str) -> List[Connection]:
        """
        Get all the connections that can provide resources to this node but filtered by resource_type
        :param resource_type: The resource type to filter by
        :return:The list of connections
        """
        return [connection for connection in self._incoming_connections if connection.resource_type == resource_type]

    def getAllOutgoingConnectionsByType(self, resource_type: str) -> List[Connection]:
        """
        Get all the connections that the node can move resources from itself to somewhere else but filtered by resource_type
        :param resource_type: The resource type to filter by
        :return:The list of connections
        """
        return [connection for connection in self._outgoing_connections if connection.resource_type == resource_type]

    def preGetResource(self, resource_type: str, amount: float) -> float:
        """
        How much resources would this node be to give if we were to actually do it.

        :param resource_type: Type of resource that is requested
        :param amount: Amount of resources needed
        :return: Amount of resources available

        .. seealso:: :py:meth:`Nodes.Node.Node.getResource` to actually request the resources
        """
        return 0

    def preGiveResource(self, resource_type: str, amount: float) -> float:
        """
        How much resources would this node be able to accept if provideResource is called.

        :param resource_type: Type of resource that is provided
        :param amount: Amount of resources that are provided
        :return: Amount of resources that could be accepted

        .. seealso:: :py:meth:`Nodes.Node.Node.giveResource` to actually provide the resources to this node
        """
        return 0

    def getResource(self, resource_type: str, amount: float) -> float:
        """
        Ask this node to provide the requested resource.

        :param resource_type: Type of resource that is requested
        :param amount: Amount of resources needed
        :return: Amount of resources available

        .. seealso:: :py:meth:`Nodes.Node.Node.preGetResource` for a way to ask how much a node could give without actually requesting it.
        """
        return 0  # By default, we don't have the resource. Go home.

    def giveResource(self, resource_type: str, amount: float) -> float:
        """
        Give resources of a certain type to this node.

        :param resource_type: Type of resource that is provided
        :param amount: Amount of resources that are provided
        :return: Amount of resources that could be accepted

        .. seealso:: :py:meth:`Nodes.Node.Node.preGiveResource` to check how much this node could accept without actually giving it.
        """
        return 0
