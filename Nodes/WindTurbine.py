from typing import List

from Nodes.FluctuatingResourceGenerator import FluctuatingResourceGenerator


class WindTurbine(FluctuatingResourceGenerator):
    def __init__(self, node_id: str,
                 amount: float,
                 amplitudes: List[float],
                 frequencies: List[float],
                 offset: float = 0,
                 **kwargs) -> None:
        defaults = {}
        defaults.update(kwargs)

        super().__init__(node_id, "energy", amount, amplitudes, frequencies, offset, **defaults)
        self._description = "Generates power from wind"
