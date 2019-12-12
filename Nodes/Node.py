from typing import List, Dict, Any

from Nodes.Connection import Connection
from Signal import signalemitter, Signal


@signalemitter
class Node:
    # TODO: Right now outside temp is hardcoded to 20 deg celcius
    outside_temp = 293.15
    """
    This is an abstract class. Most objects in the system should inherit from this base class.

    Nodes itself can be connected by Connections to move resources arround.

    Nodes can produce and require a certain amount of resources per tick.
    """
    
    preUpdateCalled = Signal()
    updateCalled = Signal()
    postUpdateCalled = Signal()

    def __init__(self, node_id: str, **kwargs) -> None:
        """
        :param node_id: Unique identifier of the node.
        """
        self._node_id = node_id
        self._incoming_connections = []  # type: List[Connection]
        self._outgoing_connections = []  # type: List[Connection]

        self._resources_required_per_tick = {}  # type: Dict[str, float]
        self._resources_received_this_tick = {}  # type: Dict[str, float]
        self._resources_produced_this_tick = {}  # type: Dict[str, float]

        # Any resources that were left from previous (ticks) that could not be left anywhere.
        self._resources_left_over = {}  # type: Dict[str, float]

        # Temperature is in kelvin (so default is 20 deg c)
        self._temperature = 293.15
        self._weight = 300.

        # How well does this node emit heat. 0 is a perfect reflector, 1 is the sun.
        self._heat_emissivity = 0.5

        # A few examples of heat_convection_coefficient all in W/m K:
        # Plastic: 0.1-0.22
        # Stainless steel: 16-24
        # Aluminum: 205 - 250
        self._heat_convection_coefficient = 10.
        # How large is the surface of this object (in M2)
        self._surface_area = 1.
        # A constant for heat.
        self.__stefan_boltzmann_constant = 5.67e-8

    def serialize(self) -> Dict[str, Any]:
        result = dict()
        result["node_id"] = self._node_id
        result["resources_received_this_tick"] = self._resources_received_this_tick
        result["resources_produced_this_tick"] = self._resources_produced_this_tick
        result["resources_left_over"] = self._resources_left_over
        result["temperature"] = self._temperature
        return result

    def deserialize(self, data: Dict[str, Any]) -> None:
        self._node_id = data["node_id"]
        self._resources_received_this_tick = data["resources_received_this_tick"]
        self._resources_produced_this_tick = data["resources_produced_this_tick"]
        self._resources_left_over = data["resources_left_over"]
        self._temperature = data["temperature"]

    @property
    def weight(self):
        return self._weight

    @property
    def temperature(self):
        return self._temperature

    def addHeat(self, heat_to_add: float) -> None:
        self._temperature += heat_to_add / self.weight

    def __repr__(self):
        return "Node ('{node_id}', a {class_name})".format(node_id = self._node_id, class_name = type(self).__name__)

    def updateReservations(self) -> None:
        pass

    def getId(self) -> str:
        return self._node_id

    def getResourcesRequiredPerTick(self) -> Dict[str, float]:
        return self._resources_required_per_tick

    def getResourcesReceivedThisTick(self) -> Dict[str, float]:
        return self._resources_received_this_tick

    def getResourcesProducedThisTick(self) -> Dict[str, float]:
        return self._resources_produced_this_tick

    def getResourceAvailableThisTick(self, resource_type: str) -> float:
        """
        Convenience function that combines the resources that this node got this tick and whatever was left over.
        It can happen that resources were requested in a previous tick, that could not be used (because of various reasons).
        Since it's super annoying to give those back, the node will just keep them in storage (and try to re-use them
        in the next tick.

        :param resource_type: Type of the resource to check for
        :return: Amount of resources of the given type that can be used this tick.
        """
        return self._resources_received_this_tick.get(resource_type.lower(), 0.) + self._resources_left_over.get(resource_type.lower(), 0.)

    def preUpdate(self) -> None:
        self.preUpdateCalled.emit(self)
        for resource_type in self._resources_required_per_tick:
            connections = self.getAllIncomingConnectionsByType(resource_type)
            if len(connections) == 0:
                # Can't get the resource at all!
                return
            total_resource_to_reserve = self._resources_required_per_tick[resource_type] - self._resources_left_over.get(resource_type, 0)
            resource_to_reserve = total_resource_to_reserve / len(connections)
            for connection in connections:
                connection.reserveResource(resource_to_reserve)

    def _getReservedResourceByType(self, resource_type: str) -> float:
        result = 0.
        for connection in self.getAllIncomingConnectionsByType(resource_type):
            result += connection.getReservedResource()
        return result

    def _provideResourceToOutogingConnections(self, resource_type: str, amount: float) -> float:
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
        while len(outgoing_connections):
            active_connection = outgoing_connections.pop()
            resources_stored = active_connection.giveResource(amount / (len(outgoing_connections) + 1))
            amount -= resources_stored
        return amount

    def _getAllReservedResources(self) -> None:
        """
        Once the planning is done, this function ensures that all reservations actually get executed.
        The results are places in the _resources_received_this_tick dict.
        """
        for resource_type in self._resources_required_per_tick:
            self._resources_received_this_tick[resource_type] = self._getReservedResourceByType(resource_type)

    def replanReservations(self) -> None:
        """
        If for whatever reason the initial reservations can not be met, this function will attempt to ask more of the
        connections that did fulfill what was asked for (hoping that those can provide more resources)
        """
        for resource_type in self._resources_required_per_tick:
            connections = self.getAllIncomingConnectionsByType(resource_type)
            total_resource_deficiency = sum([connection.getReservationDeficiency() for connection in connections])
            num_statisfied_reservations = len([connection for connection in connections if connection.isReservationStatisfied()])
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
                    connection.reserveResource(connection.reserved_requested_amount + extra_resource_to_ask_per_connection)

    def update(self) -> None:
        self.updateCalled.emit(self)
        self._getAllReservedResources()

    def postUpdate(self) -> None:
        self.postUpdateCalled.emit(self)
        for connection in self._outgoing_connections:
            connection.reset()
        self._resources_received_this_tick = {}
        self._resources_produced_this_tick = {}
        self._emitHeat()
        self._convectiveHeatTransfer()

    def _emitHeat(self) -> None:
        """
        Heat also leaves objects by grace of radiation. This is calculated by the The Stefan-Boltzmann Law
        """
        temp_diff = pow(self.outside_temp, 4) - pow(self.temperature, 4)
        heat_radiation = self.__stefan_boltzmann_constant * self._heat_emissivity * self._surface_area * temp_diff

        self.addHeat(heat_radiation)

    def _convectiveHeatTransfer(self) -> None:
        heat_convection = self._heat_convection_coefficient * self._surface_area * (self.outside_temp - self.temperature)
        self.addHeat(heat_convection)

    def requiresReplanning(self) -> bool:
        """
        Does this node need another replan step in order to get more resources.
        Do keep in mind that even if this returns false, it does not mean that it got everything that it asked for (just
        that nothing more can be done to ensure that it happens). If a node did get everything it asked, no replanning
        is needed.

        :return: If a replan is needed or not
        """
        num_statisfied_reservations = len([connection for connection in self._incoming_connections if connection.isReservationStatisfied()])
        if not num_statisfied_reservations:
            return False
        else:
            return len(self._incoming_connections) != num_statisfied_reservations

    def connectWith(self, resource_type: str, target: "Node") -> None:
        """
        Create a connection that transports the provided resource_type from this node to the provided node.
        :param resource_type: The resource that this node needs to connect.
        :param target: The node that is the target of the connection
        :return:
        """
        new_connection = Connection(origin=self, target=target, resource_type = resource_type)
        self._outgoing_connections.append(new_connection)
        target.addConnection(new_connection)

    def addConnection(self, connection: Connection) -> None:
        self._incoming_connections.append(connection)

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
