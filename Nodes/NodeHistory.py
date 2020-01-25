from threading import Lock
from typing import Dict, List

from Nodes.Node import Node


class NodeHistory:
    """
    Nodes themselves have no info about their history, they only have a state.
    But we do want some history to be stored, so that's where this comes in to play.
    The get functions of the node history are also thread safe, so they can be called from other threads / processes
    """
    def __init__(self, node: Node) -> None:
        self._node = node
        self._node.postUpdateCalled.connect(self._update)

        self._resources_produced_history = {}  # type: Dict[str, List[float]]
        self._resources_gained_history = {}  # type: Dict[str, List[float]]
        self._num_ticks_stored = 0
        self._temperature_history = []  # type: List[float]
        for resource_type in self._node.getResourcesRequiredPerTick():
            self._resources_gained_history[resource_type] = []

        self._data_lock = Lock()

        self._additional_properties_history = {}  # type: Dict[str, List[float]]

    def getNode(self) -> Node:
        return self._node

    def getNumTicksStored(self) -> int:
        return self._num_ticks_stored

    def getAdditionalPropertiesHistory(self) -> Dict[str, List[float]]:
        return self._additional_properties_history

    def getResourcesProducedHistory(self) -> Dict[str, List[float]]:
        with self._data_lock:
            return self._resources_produced_history

    def getResourcesGainedHistory(self) -> Dict[str, List[float]]:
        with self._data_lock:
            return self._resources_gained_history

    def getTemperatureHistory(self) -> List[float]:
        with self._data_lock:
            return self._temperature_history

    def _update(self, node: Node) -> None:
        with self._data_lock:
            self._num_ticks_stored += 1
            self._temperature_history.append(self._node.temperature)
            resources_received = self._node.getResourcesReceivedThisTick()
            resources_produced = self._node.getResourcesProducedThisTick()
            for resource_type in self._node.getResourcesRequiredPerTick():
                if resource_type not in resources_received:
                    self._resources_gained_history[resource_type].append(0)

            for resource_type in resources_received:
                if resource_type not in self._resources_gained_history:
                    self._resources_gained_history[resource_type] = []
                self._resources_gained_history[resource_type].append(resources_received[resource_type])

            for resource_type in resources_produced:
                if resource_type not in self._resources_produced_history:
                    self._resources_produced_history[resource_type] = []
                self._resources_produced_history[resource_type].append(resources_produced[resource_type])

            for prop in node.additional_properties:
                if prop not in self._additional_properties_history:
                    self._additional_properties_history[prop] = []
                self._additional_properties_history[prop].append(getattr(node, prop))
