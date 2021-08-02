from threading import RLock
from typing import List, Dict, Any

from Nodes.Connection import Connection
from Nodes.Modifiers.Modifier import Modifier
from Nodes.Modifiers.ModifierFactory import ModifierFactory
from Signal import signalemitter, Signal


def modifiable_property(f):
    """
    A modifiable property is one that can be modified by, you guessed it, modifiers.

    If a property has a max_{property_name}, it will also be used to clamp it's max.
    :param f:
    :return:
    """
    @property
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
    return wrapper


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

    def __init__(self, node_id: str, temperature: float = 293.15, **kwargs) -> None:
        """
        :param node_id: Unique identifier of the node.
        """
        self._node_id = node_id
        self._incoming_connections = []  # type: List[Connection]
        self._outgoing_connections = []  # type: List[Connection]

        # What resources *must* this node get in order to function?
        self._resources_required_per_tick = {}  # type: Dict[str, float]
        self._original_resources_required_per_tick = {}  # type: Dict[str, float]

        # What resources does this node want in order to function (but it could do without?)
        self._optional_resources_required_per_tick = {}  # type: Dict[str, float]
        self._original_optional_resources_required_per_tick = {}  # type: Dict[str, float]
        self._optional_resources_required_last_tick = {}  # type: Dict[str, float]

        self._resources_received_this_tick = {}  # type: Dict[str, float]
        self._resources_produced_this_tick = {}  # type: Dict[str, float]
        self._resources_provided_this_tick = {}  # type: Dict[str, float]

        self._resources_received_this_sub_tick = {} # type: Dict[str, float]

        self._resources_required_last_tick = {}  # type: Dict[str, float]
        self._resources_received_last_tick = {}  # type: Dict[str, float]
        self._resources_produced_last_tick = {}  # type: Dict[str, float]
        self._resources_provided_last_tick = {}  # type: Dict[str, float]

        # Any resources that were left from previous (ticks) that could not be left anywhere.
        self._resources_left_over = {}  # type: Dict[str, float]

        # Temperature is in kelvin
        self._temperature = temperature
        self._weight = kwargs.get("weight", 300)   # type: float

        # How well does this node emit heat. 0 is a perfect reflector, 1 is the sun.
        self._heat_emissivity = kwargs.get("heat_emissivity", 0.5)  # type: float

        # Is the node working at all?
        self._enabled = kwargs.get("enabled", True)

        self._can_be_modified = kwargs.get("can_be_modified", True)

        self._update_lock = RLock()

        # A few examples of heat_convection_coefficient all in W/m K:
        # Plastic: 0.1-0.22
        # Stainless steel: 16-24
        # Aluminum: 205 - 250
        self._heat_convection_coefficient = kwargs.get("heat_convection_coefficient", 10.)  # type: float
        # How large is the surface of this object (in M2)
        self._surface_area = kwargs.get("surface_area", 1)  # type: float
        # A constant for heat.
        self.__stefan_boltzmann_constant = 5.67e-8  # type: float

        # A list of additional properties that can be retrieved (for example, the ResourceStorage has "amount")
        # This is to notify the other observers that the property exists (for example, the NodeHistory uses this).
        # If the max value a property can take should also be communicated, the max_{property_name} is also requested
        self.additional_properties = ["health"]  # type: List[str]

        # How healthy is the node?
        self._health = 100.  # type: float
        self._max_health = 100  # type: float
        self._active = False  # type: bool
        self._max_safe_temperature = 400  # type: float

        # At what level should this node perform?
        self._performance = kwargs.get("performance", 1)  # type: float
        self._target_performance = kwargs.get("target_performance", 1)  # type: float

        self._min_performance = kwargs.get("min_performance", 1)  # type: float
        self._max_performance = kwargs.get("max_performance", 1)  # type: float

        self._has_settable_performance = True

        # How fast should this node degrade if it's above a certain temperature?
        self._temperature_degradation_speed = 10.  # type: float

        self._description = ""  # type: str
        self._custom_description = ""  # type: str

        self._modifiers = []  # type: List[Modifier]

        self._use_temperature_dependant_effectiveness_factor = False

        # Does this node change it's performance instantly?
        # a value of 1 means it changes instantly, higher values means it changes slower.
        self._performance_change_factor = 2  # type: float

        self._optimal_temperature = kwargs.get("optimal_temperature", 375) # type: float
        self._optimal_temperature_range = kwargs.get("optimal_temperature_range", 75) # type: float

        # How (in)efficient is the Node. This is only for nodes that produce something and heat at the same time.
        # An efficiency of 0 means that no heat is produced. An efficiency of 1 means that all heat of production is
        # transformed into heat. Note that this does not have an effect on the actual resources produced, just the heat
        self._temperature_efficiency = kwargs.get("temperature_efficiency", 1)  # type: float

        # Tags can be used to label a node as being of a specific type.
        # Consider options like "mechanical", "electronic", etc.
        # Certain modifiers require a certain tag to be present before they can be set on a node.
        self._tags = []  # type: List[str]

    @property
    def tags(self) -> List[str]:
        return self._tags

    @property
    def hasSettablePerformance(self):
        return self._has_settable_performance

    @property
    def isTemperatureDependant(self):
        return self._use_temperature_dependant_effectiveness_factor

    def ensureSaneValues(self) -> None:
        # This is to ensure that when custom performance is set that any updates are done.
        # Due to child classes changing how this behavior can be, it's hard to get it in the constructor.
        # As such we just let an external class ensure this bit of bookkeeping is done.
        self._original_resources_required_per_tick = self._resources_required_per_tick.copy()
        self._original_optional_resources_required_per_tick = self._optional_resources_required_per_tick.copy()
        self._resources_required_last_tick = self._resources_required_per_tick.copy()
        self._optional_resources_required_last_tick = self._optional_resources_required_per_tick.copy()
        self._setPerformance(self.performance)

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

    @property
    def can_be_modified(self) -> bool:
        return self._can_be_modified

    def getModifiers(self) -> List[Modifier]:
        return self._modifiers

    def addModifier(self, modifier: Modifier) -> None:
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

    def removeModifier(self, modifier: Modifier) -> None:
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

    @property
    def performance(self) -> float:
        return self._performance

    def _setPerformance(self, new_performance: float) -> None:
        with self._update_lock:
            self._performance = new_performance
            for resource in self._resources_required_per_tick:
                if resource not in self._original_resources_required_per_tick:
                    self._original_resources_required_per_tick[resource] = self._resources_required_per_tick[resource]

                self._resources_required_per_tick[resource] = self._original_resources_required_per_tick[
                                                                  resource] * self._performance

            for resource in self._optional_resources_required_per_tick:
                if resource not in self._original_optional_resources_required_per_tick:
                    self._original_optional_resources_required_per_tick[resource] = self._optional_resources_required_per_tick[resource]

                self._optional_resources_required_per_tick[resource] = self._original_optional_resources_required_per_tick[
                                                                  resource] * self._performance

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
        if amount < 0.:
            amount = 0.
        self._health += amount
        if self._health > self.max_health:
            self._health = self.max_health

    def damage(self, amount: float) -> None:
        self._health -= amount
        if self._health < 0:
            self._health = 0

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

    def acquireUpdateLock(self):
        self._update_lock.acquire()

    def releaseUpdateLock(self):
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
        result["resources_received_this_tick"] = self._resources_received_this_tick
        result["resources_produced_this_tick"] = self._resources_produced_this_tick
        result["resources_provided_this_tick"] = self._resources_provided_this_tick
        result["resources_left_over"] = self._resources_left_over
        result["temperature"] = self._temperature
        result["custom_description"] = self._custom_description
        result["performace"] = self._performance
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
        self._resources_received_this_tick = data["resources_received_this_tick"]
        self._resources_produced_this_tick = data["resources_produced_this_tick"]
        self._resources_provided_this_tick = data["resources_provided_this_tick"]
        self._resources_left_over = data["resources_left_over"]
        self._temperature = data["temperature"]
        self._custom_description = data.get("custom_description", "")
        self._setPerformance(data.get("performance", 1.))

        for modifier in data.get("modifiers", []):
            mod = ModifierFactory.createModifier(modifier["type"])
            if mod:
                mod.deserialize(modifier)
                self.addModifier(mod)

    @property
    def weight(self):
        return self._weight

    @modifiable_property
    def performance_change_factor(self):
        return self._performance_change_factor

    @modifiable_property
    def temperature(self):
        """
        The temperature of this node in Kelvin
        """
        return self._temperature

    def addHeat(self, heat_to_add: float, additional_weight: float = 0) -> None:
        self._temperature += heat_to_add / (self.weight - additional_weight)

    def __repr__(self):
        return "Node ('{node_id}', a {class_name})".format(node_id = self._node_id, class_name = type(self).__name__)

    def updateReservations(self) -> None:
        pass

    def getId(self) -> str:
        return self._node_id

    def getResourcesRequiredPerTick(self) -> Dict[str, float]:
        """
        Get all the resources that are required this tick. Note that this doesn't contain optional requirements!
        :return:
        """
        return self._resources_required_per_tick

    def getResourcesRequiredLastTick(self) -> Dict[str, float]:
        return self._resources_required_last_tick

    def getResourcesRequiredPreviousTick(self):
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
        return self._optional_resources_required_last_tick

    def getResourcesReceivedThisTick(self) -> Dict[str, float]:
        return self._resources_received_this_tick

    def getResourcesReceivedLastTick(self) -> Dict[str, float]:
        return self._resources_received_last_tick

    def getResourcesProducedThisTick(self) -> Dict[str, float]:
        return self._resources_produced_this_tick

    def getResourcesProducedLastTick(self) -> Dict[str, float]:
        return self._resources_produced_last_tick

    def getResourcesProvidedThisTick(self) -> Dict[str, float]:
        return self._resources_provided_this_tick

    def getResourcesProvidedLastTick(self) -> Dict[str, float]:
        return self._resources_provided_this_tick

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
        self.preUpdateCalled.emit(self)

        self._updatePerformance()
        all_resources = self.getAllResourcesRequiredPerTick()
        if self.getId() == "generator":
            print("preUpdate", all_resources)
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
        # Performance works with a target and an actual performance.
        if self.performance == self.target_performance:
            return

        new_performance = self.performance + (self.target_performance - self.performance) / max(self.performance_change_factor, 1)

        if abs(new_performance - self.target_performance) < 0.001:
            new_performance = self.target_performance

        self._setPerformance(new_performance)

    def _getReservedResourceByType(self, resource_type: str, sub_tick_modifier: float) -> float:
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
        """
        all_resources = self.getAllResourcesRequiredPerTick()
        for resource_type in all_resources:
            already_received_resources = self._resources_received_this_sub_tick.get(resource_type, 0)
            reserved_resources = self._getReservedResourceByType(resource_type, sub_tick_modifier)
            self._resources_received_this_sub_tick[resource_type] = reserved_resources + already_received_resources
            #if resource_type not in self._resources_received_this_tick:
            #    self._resources_received_this_tick[resource_type] = 0

            #self._resources_received_this_tick[resource_type] += reserved_resources + already_received_resources

    def replanReservations(self) -> None:
        """
        If for whatever reason the initial reservations can not be met, this function will attempt to ask more of the
        connections that did fulfill what was asked for (hoping that those can provide more resources)
        """
        all_resources = self.getAllResourcesRequiredPerTick()
        for resource_type in all_resources:
            connections = self.getAllIncomingConnectionsByType(resource_type)
            total_resource_deficiency = sum([connection.getReservationDeficiency() for connection in connections])
            num_statisfied_reservations = len(
                [connection for connection in connections if connection.isReservationStatisfied()])

            if num_statisfied_reservations == 0:
                extra_resource_to_ask_per_connection = 0.
            else:
                extra_resource_to_ask_per_connection = total_resource_deficiency / num_statisfied_reservations
            for connection in connections:
                if not connection.isReservationStatisfied():
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
        self.updateCalled.emit(self)
        self._getAllReservedResources(sub_tick_modifier)

    def _reEvaluateIsActive(self) -> bool:
        for resource_required, amount_needed in self._resources_required_per_tick.items():
            if self._resources_received_this_tick.get(resource_required, 0) != amount_needed:
                return False
        return True

    def postUpdate(self) -> None:
        self._active = self._reEvaluateIsActive()
        self._emitHeat()
        self._convectiveHeatTransfer()
        self._dealDamageFromHeat()
        self._resources_required_last_tick = self._resources_required_per_tick.copy()
        self._resources_received_last_tick = self._resources_received_this_tick.copy()
        self._optional_resources_required_last_tick = self._optional_resources_required_per_tick.copy()
        self._resources_produced_last_tick = self._resources_produced_this_tick.copy()
        self._resources_provided_last_tick = self._resources_provided_this_tick.copy()

        self.postUpdateCalled.emit(self)
        for connection in self._outgoing_connections:
            connection.reset()
        self._resources_received_this_tick = {}
        self._resources_received_this_sub_tick = {}
        self._resources_produced_this_tick = {}
        self._resources_provided_this_tick = {}

    def updateModifiers(self) -> None:
        # Update the timers of the modifiers (and remove them if they have expired)
        for modifier in self._modifiers:
            modifier.update()

    def _emitHeat(self) -> None:
        """
        Heat also leaves objects by grace of radiation. This is calculated by the The Stefan-Boltzmann Law
        """
        temp_diff = pow(self.outside_temp, 4) - pow(self.temperature, 4)
        heat_radiation = self.__stefan_boltzmann_constant * self.heat_emissivity * self._surface_area * temp_diff
        self.addHeat(heat_radiation)

        if heat_radiation < 0:
            if self._temperature < self.outside_temp:
                # We were warmer than the outside before, but no amount of radiation can make us go lower!
                self._temperature = self.outside_temp

    def _convectiveHeatTransfer(self) -> None:
        delta_temp = self.outside_temp - self.temperature
        heat_convection = self.heat_convection_coefficient * self._surface_area * delta_temp
        self.addHeat(heat_convection)
        if heat_convection < 0: # Cooling down happend.
            if self._temperature < self.outside_temp:
                # We were warmer than the outside before, but no amount of convection can make us go lower!
                self._temperature = self.outside_temp

    def _dealDamageFromHeat(self) -> None:
        delta_temp = self.temperature - self._max_safe_temperature
        if delta_temp <= 0:
            return
        self._health -= self.temperature_degradation_speed * (delta_temp / self._max_safe_temperature)
        if self._health < 0:
            self._health = 0

    def _getHealthEffectivenessFactor(self) -> float:
        health_factor = self._health / 100.
        # This makes the effectiveness a bit less punishing.
        # 75% health: 90% effectiveness
        # 50% health: 75% effectiveness
        # 25% health: 50% effectiveness
        # 10% health: 25% effectiveness
        # 1%  health: ~3% effectiveness
        factor = (-((health_factor + 0.5) / (health_factor + 0.5) ** 2.) + 2) / 1.333333333333333
        return factor

    @property
    def health_effectiveness_factor(self) -> float:
        """
        If the node doesn't have a temperature dependant effiency, will be the same as effectivenss_factor
        The main reason you would want to use this instead of the effectivenss factor, is when you only want to take
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
        temperature_difference = abs(self._temperature - self.optimal_temperature)
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
        num_statisfied_reservations = len(
            [connection for connection in self._incoming_connections if connection.isReservationStatisfied()])

        if not num_statisfied_reservations:
            return False
        return len(self._incoming_connections) != num_statisfied_reservations

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
        with self._update_lock:
            self._incoming_connections.append(connection)

    def getAllOutgoingConnections(self) -> List[Connection]:
        return self._outgoing_connections

    def getAllIncomingConnections(self) -> List[Connection]:
        return self._incoming_connections

    def getAllIncomingConnectionsByType(self, resource_type: str) -> List[Connection]:
        return [connection for connection in self._incoming_connections if connection.resource_type == resource_type]

    def getAllOutgoingConnectionsByType(self, resource_type: str) -> List[Connection]:
        return [connection for connection in self._outgoing_connections if connection.resource_type == resource_type]

    def preGetResource(self, resource_type: str, amount: float) -> float:
        """
        How much resources would this node be to give if we were to actually do it.

        :param resource_type: Type of resource that is requested
        :param amount: Amount of resources needed
        :return: Amount of resources available
        """
        return 0

    def preGiveResource(self, resource_type: str, amount: float) -> float:
        """
        How much resources would this node be able to accept if provideResource is called.

        :param resource_type: Type of resource that is provided
        :param amount: Amount of resources that are provided
        :return: Amount of resources that could be accepted
        """
        return 0

    def getResource(self, resource_type: str, amount: float) -> float:
        return 0  # By default, we don't have the resource. Go home.

    def giveResource(self, resource_type: str, amount: float) -> float:
        return 0
