from Nodes.Modifiers.Modifier import Modifier


class EmergencyShutdownModifier(Modifier):
    def __init__(self, duration: int) -> None:
        super().__init__(factors = {"min_performance": 0, "max_performance": 0}, duration = duration)

        self._name = "Emergency Shutdown"
        self._abbreviation = "ESD"

        self._description = "Completely disable a device, even if it can otherwise not be disabled. As long as this" \
                            "modifier is active, the device is completely shut down"




