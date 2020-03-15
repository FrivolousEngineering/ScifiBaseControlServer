
import dbus
import dbus.service
from typing import List, Dict

from Nodes.Modifiers.ModifierFactory import createModifier
from Nodes.NodeEngine import NodeEngine


class DBusService(dbus.service.Object):
    def __init__(self, engine: NodeEngine) -> None:
        self._bus = dbus.SessionBus()
        super().__init__(
            bus_name = dbus.service.BusName("com.frivengi.nodes", self._bus),
            object_path = "/com/frivengi/nodes"
        )

        self._node_engine = engine

    @dbus.service.method("com.frivengi.nodes", in_signature="ss")
    def addModifierToNode(self, node_id: str, modifier_type: str) -> None:
        node = self._node_engine.getNodeById(node_id)
        modifier = createModifier(modifier_type)
        if node and modifier:
            node.addModifier(modifier)

    @dbus.service.method("com.frivengi.nodes", out_signature="aa{sv}", in_signature="s")
    def getActiveModifiers(self, node_id):
        node = self._node_engine.getNodeById(node_id)
        if not node:
            return []

        return [{"name": modifier.name, "duration": modifier.duration} for modifier in node.getModifiers()]

    @dbus.service.method("com.frivengi.nodes", out_signature="d", in_signature="s")
    def getNodeTemperature(self, node_id: str) -> float:
        node = self._node_engine.getNodeById(node_id)
        if node:
            return node.temperature
        return -9000.

    @dbus.service.method("com.frivengi.nodes", out_signature="s", in_signature="s")
    def getNodeDescription(self, node_id: str) -> str:
        node = self._node_engine.getNodeById(node_id)
        if node:
            return node.description
        return ""

    @dbus.service.method("com.frivengi.nodes", in_signature="s", out_signature="d")
    def getHeatEmissivity(self, node_id) -> float:
        node = self._node_engine.getNodeById(node_id)
        if node:
            return node.heat_emissivity
        return 0.

    @dbus.service.method("com.frivengi.nodes", in_signature="s", out_signature="d")
    def getSurfaceArea(self, node_id):
        node = self._node_engine.getNodeById(node_id)
        if node:
            return node.surface_area
        return 0.

    @dbus.service.method("com.frivengi.nodes", in_signature="s", out_signature="d")
    def getHeatConvection(self, node_id):
        node = self._node_engine.getNodeById(node_id)
        if node:
            return node.heat_convection_coefficient
        return 0.

    @dbus.service.method("com.frivengi.nodes", in_signature="s", out_signature="d")
    def getMaxSafeTemperature(self, node_id):
        node = self._node_engine.getNodeById(node_id)
        if node:
            return node.max_safe_temperature
        return 0.

    @dbus.service.method("com.frivengi.nodes", in_signature="sd")
    def setPerformance(self, node_id, performance):
        node = self._node_engine.getNodeById(node_id)
        if node:
            node.performance = performance

    @dbus.service.method("com.frivengi.nodes", in_signature="s", out_signature="d")
    def getPerformance(self, node_id):
        node = self._node_engine.getNodeById(node_id)
        if node:
            return node.performance
        return 0

    @dbus.service.method("com.frivengi.nodes", out_signature="d", in_signature="s")
    def isNodeActive(self, node_id: str) -> bool:
        node = self._node_engine.getNodeById(node_id)
        if node:
            return node.active
        return False

    @dbus.service.method("com.frivengi.nodes", out_signature="ad", in_signature="s")
    def getNodeTemperatureHistory(self, node_id: str) -> List[float]:
        history = self._node_engine.getNodeHistoryById(node_id)
        if history:
            return history.getTemperatureHistory()
        return []

    @dbus.service.method("com.frivengi.nodes", out_signature="a{sv}", in_signature="s")
    def getResourcesGainedHistory(self, node_id: str):
        history = self._node_engine.getNodeHistoryById(node_id)
        if history:
            return dbus.Dictionary(history.getResourcesGainedHistory(), signature='sv')
        return {}

    @dbus.service.method("com.frivengi.nodes", out_signature="a{sv}", in_signature="s")
    def getResourcesProducedHistory(self, node_id: str):
        history = self._node_engine.getNodeHistoryById(node_id)
        if history:
            return dbus.Dictionary(history.getResourcesProducedHistory(), signature='sv')
        return {}

    @dbus.service.method("com.frivengi.nodes", out_signature="ad", in_signature="ss")
    def getAdditionalPropertyHistory(self, node_id: str, prop: str) -> List[float]:
        history = self._node_engine.getNodeHistoryById(node_id)
        if history:
            return history.getAdditionalPropertiesHistory().get(prop, [])
        return []

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

    @dbus.service.method("com.frivengi.nodes")
    def doTick(self) -> None:
        self._node_engine.doTick()

    @dbus.service.method("com.frivengi.nodes", in_signature="s", out_signature="d")
    def getAmountStored(self, node_id: str) -> float:
        node = self._node_engine.getNodeById(node_id)
        if not node:
            return -1
        try:
            return node.amount_stored  # type: ignore
        except AttributeError:
            return -1

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
    def checkAlive(self):
        """
        Yes, this serves a purpose. As the name implies, this is used to check if this service is still alive.
        It doesn't actually need to return an answer, since if the service isn't there, we get an exception.
        :return:
        """
        return

    @dbus.service.method("com.frivengi.nodes", in_signature="s", out_signature="d")
    def getMinPerformance(self, node_id):
        node = self._node_engine.getNodeById(node_id)
        if node:
            return node.min_performance
        return 1.

    @dbus.service.method("com.frivengi.nodes", in_signature="s", out_signature="d")
    def getMaxPerformance(self, node_id):
        node = self._node_engine.getNodeById(node_id)
        if node:
            return node.max_performance
        return 1.
