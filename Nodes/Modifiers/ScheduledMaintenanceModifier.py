from Nodes.Modifiers.Modifier import Modifier


class ScheduledMaintenanceModifier(Modifier):
    def __init__(self, amount_to_repair_per_turn: float, duration: int) -> None:
        super().__init__(duration = duration)
        self._amount_to_repair_per_turn = amount_to_repair_per_turn
        self._name = "Scheduled Maintenance"
        self._abbreviation = "SMA"

        self._description = "Make significant headway with repairing a device by disabling it while it's in operation"

    def update(self) -> None:
        super().update()

        node = self._node
        if node is not None:
            node.repair(self._amount_to_repair_per_turn)