
import dbus
import dbus.service
from typing import List, Dict, Optional, Union

from Nodes.Modifiers.ModifierFactory import ModifierFactory
from Nodes.NodeEngine import NodeEngine


class NodesDBusService(dbus.service.Object):
    def __init__(self, engine: NodeEngine, session_bus: Optional[dbus.SessionBus] = None, bus_name: Optional[dbus.service.BusName] = None) -> None:
        """
        The DBUS Service exposes a large number of properties from the NodeEngine to DBUS.

        This enables other services (A web service) to poll for this data. Although this does create some overhead, it
        has the major advantage that it separates the systems (So if one of the services breaks, it can be re-spawned
        without breaking the others)

        :param engine: The engine this service is listening to
        :param session_bus:
        :param bus_name:
        """
        if session_bus is None:
            self._bus = dbus.SessionBus()
        else:
            self._bus = session_bus

        if bus_name is None:
            self._bus_name = dbus.service.BusName("com.frivengi.nodes", self._bus)
        else:
            self._bus_name = bus_name

        self._object_path = "/com/frivengi/nodes"
        self._node_engine = engine

        super().__init__(
            bus_name=self._bus_name,
            object_path=self._object_path
        )

    @dbus.service.method("com.frivengi.nodes", in_signature="ss", out_signature="b")
    def addModifierToNode(self, node_id: str, modifier_type: str) -> bool:
        node = self._node_engine.getNodeById(node_id)
        modifier = ModifierFactory.createModifier(modifier_type)

        if node and modifier:
            node.addModifier(modifier)
            return True
        return False

    @dbus.service.method("com.frivengi.nodes", out_signature="aa{sv}", in_signature="s")
    def getActiveModifiers(self, node_id: str) -> List[Dict[str, Union[str, int]]]:
        """
        Get the modifiers that are currently attached to this node.
        Due to constraints of DBUS, this only provides you with some subset of the data in dict form.
        :param node_id: ID of the node to get.
        :return: List of dicts that contain the name and duration of the found modifiers.
        """
        node = self._node_engine.getNodeById(node_id)
        if not node:
            return []

        return [{"name": modifier.name, "duration": modifier.duration, "abbreviation": modifier.abbreviation, "type": type(modifier).__name__} for modifier in node.getModifiers()]

    @dbus.service.method("com.frivengi.nodes", out_signature="d", in_signature="s")
    def getTemperature(self, node_id: str) -> float:
        node = self._node_engine.getNodeById(node_id)
        if node:
            return node.temperature
        return -9000.

    @dbus.service.method("com.frivengi.nodes", out_signature="s", in_signature="s")
    def getDescription(self, node_id: str) -> str:
        node = self._node_engine.getNodeById(node_id)
        if node:
            return node.description
        return ""

    @dbus.service.method("com.frivengi.nodes", in_signature="s")
    def getCustomDescription(self, node_id: str) -> str:
        node = self._node_engine.getNodeById(node_id)
        if node:
            return node.custom_description
        return ""

    @dbus.service.method("com.frivengi.nodes", in_signature="s", out_signature="d")
    def getHeatEmissivity(self, node_id) -> float:
        node = self._node_engine.getNodeById(node_id)
        if node:
            return node.heat_emissivity
        return 0.

    @dbus.service.method("com.frivengi.nodes", in_signature="s", out_signature="d")
    def getSurfaceArea(self, node_id: str) -> float:
        node = self._node_engine.getNodeById(node_id)
        if node:
            return node.surface_area
        return 0.

    @dbus.service.method("com.frivengi.nodes", in_signature="s", out_signature="d")
    def getHeatConvectionCoefficient(self, node_id: str) -> float:
        node = self._node_engine.getNodeById(node_id)
        if node:
            return node.heat_convection_coefficient
        return 0.

    @dbus.service.method("com.frivengi.nodes", in_signature="s", out_signature="d")
    def getMaxSafeTemperature(self, node_id: str) -> float:
        node = self._node_engine.getNodeById(node_id)
        if node:
            return node.max_safe_temperature
        return 0.

    @dbus.service.method("com.frivengi.nodes", in_signature="sd")
    def setTargetPerformance(self, node_id: str, performance: float) -> None:
        node = self._node_engine.getNodeById(node_id)
        if node:
            node.target_performance = performance

    @dbus.service.method("com.frivengi.nodes", in_signature="s", out_signature="d")
    def getPerformance(self, node_id: str) -> float:
        node = self._node_engine.getNodeById(node_id)
        if node:
            return node.performance
        return 0.

    @dbus.service.method("com.frivengi.nodes", in_signature="s", out_signature="d")
    def getTargetPerformance(self, node_id: str) -> float:
        node = self._node_engine.getNodeById(node_id)
        if node:
            return node.target_performance
        return 0.

    @dbus.service.method("com.frivengi.nodes", in_signature="s", out_signature="b")
    def hasSettablePerformance(self, node_id: str) -> bool:
        node = self._node_engine.getNodeById(node_id)
        if node:
            return node.hasSettablePerformance
        return False

    @dbus.service.method("com.frivengi.nodes", out_signature="d", in_signature="s")
    def isNodeActive(self, node_id: str) -> bool:
        node = self._node_engine.getNodeById(node_id)
        if node:
            return node.active
        return False

    @dbus.service.method("com.frivengi.nodes", out_signature="ad", in_signature="s")
    def getTemperatureHistory(self, node_id: str) -> List[float]:
        history = self._node_engine.getNodeHistoryById(node_id)
        if history:
            return history.getTemperatureHistory()
        return []

    @dbus.service.method("com.frivengi.nodes", out_signature="a{sv}", in_signature="s")
    def getResourcesGainedHistory(self, node_id: str) -> Dict:
        history = self._node_engine.getNodeHistoryById(node_id)
        if history:
            return dbus.Dictionary(history.getResourcesGainedHistory(), signature='sv')
        return {}

    @dbus.service.method("com.frivengi.nodes", out_signature="a{sv}", in_signature="s")
    def getResourcesProducedHistory(self, node_id: str) -> Dict:
        history = self._node_engine.getNodeHistoryById(node_id)
        if history:
            return dbus.Dictionary(history.getResourcesProducedHistory(), signature='sv')
        return {}

    @dbus.service.method("com.frivengi.nodes", out_signature="a{sv}", in_signature="s")
    def getResourcesProvidedHistory(self, node_id: str) -> Dict:
        history = self._node_engine.getNodeHistoryById(node_id)
        if history:
            return dbus.Dictionary(history.getResourcesProvidedHistory(), signature='sv')
        return {}

    @dbus.service.method("com.frivengi.nodes", out_signature="ad", in_signature="ss")
    def getAdditionalPropertyHistory(self, node_id: str, prop: str) -> List[float]:
        history = self._node_engine.getNodeHistoryById(node_id)
        if history:
            return history.getAdditionalPropertiesHistory().get(prop, [])
        return []

    @dbus.service.method("com.frivengi.nodes", in_signature="s", out_signature="d")
    def getHistoryOffset(self, node_id: str):
        """
        Not all data of the entire history is stored (because that would get out of hand).
        In order to still display the data correctly, we track the amount of ticks that we deleted
        :param node_id:
        :return:
        """
        history = self._node_engine.getNodeHistoryById(node_id)
        if history:
            return history.getTickOffset()
        return 0

    @dbus.service.method("com.frivengi.nodes", out_signature="as", in_signature="s")
    def getAdditionalProperties(self, node_id: str) -> List[str]:
        node = self._node_engine.getNodeById(node_id)
        if not node:
            return []
        return node.additional_properties

    @dbus.service.method("com.frivengi.nodes", in_signature="ss", out_signature="d")
    def getAdditionalPropertyValue(self, node_id: str, prop: str) -> float:
        node = self._node_engine.getNodeById(node_id)
        if not node:
            return -1
        try:
            return getattr(node, prop)
        except AttributeError:
            return -1

    @dbus.service.method("com.frivengi.nodes", in_signature="ss", out_signature="d")
    def getMaxAdditionalPropertyValue(self, node_id, prop: str) -> float:
        node = self._node_engine.getNodeById(node_id)
        if not node:
            return -1
        try:
            return getattr(node, "max_" + prop)
        except AttributeError:
            return -1

    @dbus.service.method("com.frivengi.nodes", out_signature="as")
    def getAllNodeIds(self) -> List[str]:
        return self._node_engine.getAllNodeIds()

    @dbus.service.method("com.frivengi.nodes", in_signature="s", out_signature="b")
    def doesNodeExist(self, node_id) -> bool:
        return node_id in self._node_engine.getAllNodeIds()

    @dbus.service.method("com.frivengi.nodes")
    def doTick(self) -> None:
        self._node_engine.doTick()

    @dbus.service.method("com.frivengi.nodes", out_signature = "v")
    def getCurrentTick(self) -> int:
        return self._node_engine.tick_count

    @dbus.service.method("com.frivengi.nodes", in_signature="s", out_signature="b")
    def isNodeEnabled(self, node_id: str) -> bool:
        node = self._node_engine.getNodeById(node_id)
        if not node:
            return False
        return node.enabled

    @dbus.service.method("com.frivengi.nodes", in_signature="sb")
    def setNodeEnabled(self, node_id: str, enabled: bool):
        node = self._node_engine.getNodeById(node_id)
        if node:
            node.enabled = bool(enabled)

    @dbus.service.method("com.frivengi.nodes", out_signature="aa{sv}", in_signature="s")
    def getIncomingConnections(self, node_id) -> List[Dict[str, str]]:
        node = self._node_engine.getNodeById(node_id)
        if node:
            all_connections = node.getAllIncomingConnections()
            return [{"target": connection.target.getId(),
                     "origin": connection.origin.getId(),
                     "resource_type": connection.resource_type}
                    for connection in all_connections]
        return []

    @dbus.service.method("com.frivengi.nodes", out_signature="aa{sv}", in_signature="s")
    def getOutgoingConnections(self, node_id) -> List[Dict[str, str]]:
        node = self._node_engine.getNodeById(node_id)
        if node:
            all_connections = node.getAllOutgoingConnections()
            return [{"target": connection.target.getId(),
                     "origin": connection.origin.getId(),
                     "resource_type": connection.resource_type}
                    for connection in all_connections]
        return []

    @dbus.service.method("com.frivengi.nodes")
    def checkAlive(self) -> None:
        """
        Yes, this serves a purpose. As the name implies, this is used to check if this service is still alive.
        It doesn't actually need to return an answer, since if the service isn't there, we get an exception.
        :return:
        """
        return

    @dbus.service.method("com.frivengi.nodes", in_signature="s", out_signature="d")
    def getMinPerformance(self, node_id: str) -> float:
        node = self._node_engine.getNodeById(node_id)
        if node:
            return node.min_performance
        return 1.

    @dbus.service.method("com.frivengi.nodes", in_signature="s", out_signature="d")
    def getMaxPerformance(self, node_id: str) -> float:
        node = self._node_engine.getNodeById(node_id)
        if node:
            return node.max_performance
        return 1.

    @dbus.service.method("com.frivengi.nodes", in_signature="s", out_signature="b")
    def getIsTemperatureDependant(self, node_id: str) -> bool:
        node = self._node_engine.getNodeById(node_id)
        if node:
            return node.isTemperatureDependant
        return False

    @dbus.service.method("com.frivengi.nodes", in_signature="s", out_signature="d")
    def getOptimalTemperature(self, node_id: str) -> float:
        node = self._node_engine.getNodeById(node_id)
        if node:
            return node.optimal_temperature
        return -1

    @dbus.service.method("com.frivengi.nodes", out_signature="a{sv}", in_signature="s")
    def getResourcesRequired(self, node_id: str):
        node = self._node_engine.getNodeById(node_id)
        if node:
            return node.getResourcesRequiredLastTick()
        return {}

    @dbus.service.method("com.frivengi.nodes", out_signature="a{sv}", in_signature="s")
    def getResourcesReceived(self, node_id: str):
        node = self._node_engine.getNodeById(node_id)
        if node:
            return node.getResourcesReceivedLastTick()
        return {}

    @dbus.service.method("com.frivengi.nodes", out_signature="a{sv}", in_signature="s")
    def getOptionalResourcesRequired(self, node_id: str):
        node = self._node_engine.getNodeById(node_id)
        if node:
            return node.getOptionalResourcesRequiredLastTick()
        return {}

    @dbus.service.method("com.frivengi.nodes", out_signature="a{sv}", in_signature="s")
    def getResourcesProduced(self, node_id: str):
        node = self._node_engine.getNodeById(node_id)
        if node:
            return node.getResourcesProducedLastTick()
        return {}

    @dbus.service.method("com.frivengi.nodes", out_signature="as", in_signature="s")
    def getSupportedModifiers(self, node_id: str):
        node = self._node_engine.getNodeById(node_id)
        if node:
            return ModifierFactory.getSupportedModifiersForNode(node)
        return []

    @dbus.service.method("com.frivengi.nodes", in_signature="s", out_signature="d")
    def getEffectivenessFactor(self, node_id: str):
        node = self._node_engine.getNodeById(node_id)
        if node:
            return node.effectiveness_factor
        else:
            return 1

    @dbus.service.method("com.frivengi.nodes", in_signature="s", out_signature="s")
    def getLabel(self, node_id: str):
        node = self._node_engine.getNodeById(node_id)
        if node:
            return node.label
        else:
            return "Unknown"