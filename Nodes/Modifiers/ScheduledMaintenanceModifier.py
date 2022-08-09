from Nodes.Modifiers.Modifier import Modifier


class ScheduledMaintenanceModifier(Modifier):
    def __init__(self, duration: int) -> None:
        super().__init__(factors = {"min_performance": 0, "max_performance": 0}, duration = duration)
        self._amount_to_repair_per_turn = 4
        self._name = "Scheduled Maintenance"
        self._abbreviation = "SMA"

        self._description = "Make significant headway with repairing a device by disabling it while it's in operation"

        self._required_engineering_level = 2

    def update(self) -> None:
        super().update()

        node = self._node
        if node is not None:
            node.repair(self._amount_to_repair_per_turn)