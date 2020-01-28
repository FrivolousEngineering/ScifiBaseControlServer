from Nodes.ResourceGenerator import ResourceGenerator
import math


class FluctuatingResourceGenerator(ResourceGenerator):
    def __init__(self, node_id: str, resource_type: str, amount: float, amplitude: float, frequency: float,
                 **kwargs) -> None:
        super().__init__(node_id, resource_type, amount)
        self._tick_count = 0
        self._original_amount = amount
        self._amplitude = amplitude
        self._frequency = frequency

    def postUpdate(self) -> None:
        super().postUpdate()

        self._amount = math.sin(self._frequency * self._tick_count / math.pi) * self._amplitude + self._original_amount

        self._tick_count += 1