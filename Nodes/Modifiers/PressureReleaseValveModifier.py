from Nodes.Modifiers.Modifier import Modifier


class PressureReleaseValveModifier(Modifier):
    def __init__(self, duration: int) -> None:
        super().__init__(factors = {"temperature_degradation_speed": 0.5, "max_performance": 0.5}, duration = duration)
        self._name = "Pressure Release Valve"
        self._abbreviation = "PRV"

        self._required_tag = "fuel"