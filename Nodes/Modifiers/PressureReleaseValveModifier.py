from Nodes.Modifiers.Modifier import Modifier


class PressureReleaseValveModifier(Modifier):
    def __init__(self, duration: int) -> None:
        super().__init__(factors = {"temperature_degradation_speed": 0.5, "max_performance": 0.5}, duration = duration)
        self._name = "Pressure Release Valve"
        self._abbreviation = "PRV"

        self._required_tag = "fuel"

        self._description = "Tweak the pressure release valves on this device. This will greatly decrease the max perfor" \
                            "mance, but will make it greatly more resistant to damage from heat. As such, this is best" \
                            "done when a device is overheating, but you want to delay repairing."