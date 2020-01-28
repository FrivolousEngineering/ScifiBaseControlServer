from typing import Dict, Any

from Nodes.ResourceGenerator import ResourceGenerator
import math


class FluctuatingResourceGenerator(ResourceGenerator):
    def __init__(self, node_id: str, resource_type: str, amount: float, amplitude: float, frequency: float,
                 offset: float = 0, **kwargs) -> None:
        super().__init__(node_id, resource_type, amount)
        self._tick_count = 0
        self._original_amount = amount
        self._amplitude = amplitude
        self._frequency = frequency
        self._offset = offset

    def serialize(self) -> Dict[str, Any]:
        result = super().serialize()
        result["original_amount"] = self._original_amount
        result["tick"] = self._tick_count
        return result

    def deserialize(self, data: Dict[str, Any]) -> None:
        super().deserialize(data)
        self._original_amount = data["original_amount"]
        self._tick_count = data["tick"]

    def postUpdate(self) -> None:
        super().postUpdate()
        tick_count = (self._tick_count + self._offset) / (0.5 * math.pi)

        self._amount = math.sin(10 * self._frequency * tick_count) * self._amplitude + self._original_amount

        self._tick_count += 1
