from threading import Lock
from typing import Dict, List, Deque, Any
from collections import deque

from Nodes.Node import Node
from Nodes.Util import enforcePositive


class NodeHistory:
    """
    Nodes themselves have no info about their history, they only have a state.
    But we do want some history to be stored, so that's where this comes in to play.
    The get functions of the node history are also thread safe, so they can be called from other threads / processes
    """
    def __init__(self, node: Node) -> None:
        self._node = node
        self._node.postUpdateCalled.connect(self._update)

        self._max_elements_to_store = 50

        self._resources_produced_history = {}  # type: Dict[str, Deque[float]]
        self._resources_gained_history = {}  # type: Dict[str, Deque[float]]
        self._resources_provided_history = {}  # type: Dict[str, Deque[float]]
        self._num_ticks_stored = 0
        self._temperature_history = self._createDeque()  # type: Deque[float]

        for resource_type in self._node.getResourcesRequiredPerTick():
            self._resources_gained_history[resource_type] = self._createDeque()

        self._data_lock = Lock()

        self._additional_properties_history = {}  # type: Dict[str, Deque[float]]

    def _createDeque(self, data: List[float] = None) -> Deque[float]:
        if data is None:
            data = []
        return deque(data, self._max_elements_to_store)

    def getNode(self) -> Node:
        return self._node

    def serialize(self) -> Dict[str, Any]:
        """
        Serialize this nodeHistory so that it can be stored somewhere (eg; save to file)
        :return: A dict with keys for the attribute.
        """
        result = {}  # type: Dict[str, Any]
        result["resources_produced_history"] = self._convertDequeDictToListDict(self._resources_produced_history)
        result["resources_gained_history"] = self._convertDequeDictToListDict(self._resources_gained_history)
        result["resources_provided_history"] = self._convertDequeDictToListDict(self._resources_provided_history)
        result["temperature_history"] = list(self._temperature_history)
        return result

    def deserialize(self, data: Dict[str, Any]) -> None:
        """
        Restore the data of a node from serialized information. (eg: load from file)
        :param data:
        """
        self._resources_produced_history = {}
        for produced_resource_key, values in data["resources_produced_history"].items():
            self._resources_produced_history[produced_resource_key] = self._createDeque(values)

        for gained_resource_key, values in data["resources_gained_history"].items():
            self._resources_gained_history[gained_resource_key] = self._createDeque(values)

        for gained_resource_key, values in data["resources_provided_history"].items():
            self._resources_provided_history[gained_resource_key] = self._createDeque(values)

        self._temperature_history = self._createDeque(data["temperature_history"])

    def getTickOffset(self) -> int:
        """
        Since not all data is stored, it could be that there is an offset.
        :return:
        """
        return int(enforcePositive(self._num_ticks_stored - self._max_elements_to_store))

    @staticmethod
    def _convertDequeDictToListDict(deque_dict: Dict[str, Deque[float]]) -> Dict[str, List[float]]:
        return {key: list(value) for key, value in deque_dict.items()}

    def getAdditionalPropertiesHistory(self) -> Dict[str, List[float]]:
        with self._data_lock:
            return self._convertDequeDictToListDict(self._additional_properties_history)

    def getResourcesProducedHistory(self) -> Dict[str, List[float]]:
        with self._data_lock:
            return self._convertDequeDictToListDict(self._resources_produced_history)

    def getResourcesGainedHistory(self) -> Dict[str, List[float]]:
        with self._data_lock:
            return self._convertDequeDictToListDict(self._resources_gained_history)

    def getResourcesProvidedHistory(self) -> Dict[str, List[float]]:
        with self._data_lock:
            return self._convertDequeDictToListDict(self._resources_provided_history)

    def getTemperatureHistory(self) -> List[float]:
        with self._data_lock:
            return list(self._temperature_history)

    def _update(self, node: Node) -> None:
        with self._data_lock:
            self._num_ticks_stored += 1
            self._temperature_history.append(self._node.temperature)
            resources_received = self._node.getResourcesReceivedThisTick()
            resources_produced = self._node.getResourcesProducedThisTick()
            resources_provided = self._node.getResourcesProvidedThisTick()

            for resource_type in self._node.getResourcesRequiredPerTick():
                if resource_type not in resources_received:
                    self._resources_gained_history[resource_type].append(0)

            for resource_type in resources_received:
                if resource_type not in self._resources_gained_history:
                    self._resources_gained_history[resource_type] = self._createDeque()
                self._resources_gained_history[resource_type].append(resources_received[resource_type])

            for resource_type in resources_produced:
                if resource_type not in self._resources_produced_history:
                    self._resources_produced_history[resource_type] = self._createDeque()
                self._resources_produced_history[resource_type].append(resources_produced[resource_type])

            for resource_type in resources_provided:
                if resource_type not in self._resources_provided_history:
                    self._resources_provided_history[resource_type] = self._createDeque()
                self._resources_provided_history[resource_type].append(resources_provided[resource_type])

            for prop in node.additional_properties:
                if prop not in self._additional_properties_history:
                    self._additional_properties_history[prop] = self._createDeque()
                self._additional_properties_history[prop].append(getattr(node, prop))
