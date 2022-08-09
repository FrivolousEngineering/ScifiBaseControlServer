from Nodes.Modifiers.Modifier import Modifier


class EmergencyShutdownModifier(Modifier):
    def __init__(self, duration: int) -> None:
        super().__init__(factors = {"min_performance": 0, "max_performance": 0, "target_performance": 0, "performance": 0}, duration = duration)

        self._name = "Emergency Shutdown"
        self._abbreviation = "ESD"
        self._initial_performance = 0
        self._description = "Completely disable a device, even if it can otherwise not be disabled. As long as this" \
                            "modifier is active, the device is completely shut down"

    def _onModifierAdded(self) -> None:
        node = self._node
        if node is not None:
            self._initial_performance = node.target_performance
            node.set

    def _onModifierRemoved(self) -> None:
        node = self._node

        if node is not None:
            node.target_performance = self._initial_performance


