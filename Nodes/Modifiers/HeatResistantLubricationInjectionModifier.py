

from Nodes.Modifiers.Modifier import Modifier


class HeatResistantLubricationInjectionModifier(Modifier):
    def __init__(self, duration: int) -> None:
        super().__init__(factors = {"performance_change_factor": 1.25, "max_performance": 0.9}, modifiers = {"max_safe_temperature": 50}, duration = duration)

        self._name = "Heat Resistant Lubrication Injection"
        self._abbreviation = "HLI"

        self._required_tag = "mechanical"
        self._description = "Inject the device with a more heat resistant lubrication. This will decrease the max perfo" \
                            "rmance as well as making it a bit more sluggish to respond to performance changes. It does" \
                            " ensure that higher temperatures are needed before it starts getting damage."
