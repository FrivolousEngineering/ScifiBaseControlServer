

from Nodes.Modifiers.Modifier import Modifier


class HeatResistantLubricationInjection(Modifier):
    def __init__(self, duration: int) -> None:
        super().__init__(factors = {"performance_change_factor": 0.75, "max_performance": 0.9}, modifiers = {"max_safe_temperature": 50}, duration = duration)

        self._name = "Heat Resistant Lubrication Injection"
        self._abbreviation = "HLI"

        self._required_tag = "mechanical"
