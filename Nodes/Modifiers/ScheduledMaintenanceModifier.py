from Nodes.Modifiers.Modifier import Modifier


class ScheduledMaintenanceModifier(Modifier):
    def __init__(self, duration: int) -> None:
        super().__init__(factors = {"min_performance": 0, "max_performance": 0, "target_performance": 0}, duration = duration)
        self._amount_to_repair_per_turn = 4
        self._name = "Scheduled Maintenance"
        self._abbreviation = "SMA"

        self._description = "Make significant headway with repairing a device by disabling it while it's in " \
                            "operation. The amount repaired will depend on the current performance of the machine." \
                            "As such, it can be beneficial to schedule multiple maintenance modifiers after each other" \
                            "so that there is less downtime from the device winding down."

        self._required_engineering_level = 2
        self._initial_performance = 0

    def update(self) -> None:
        super().update()

        node = self._node
        if node is not None:
            final_amount_to_repair = max(1 - node.performance, 0) * self._amount_to_repair_per_turn
            node.repair(final_amount_to_repair)

    def _onModifierAdded(self) -> None:
        node = self._node
        if node is not None:
            self._initial_performance = node.target_performance

    def _onModifierRemoved(self) -> None:
        node = self._node

        if node is not None:
            node.target_performance = self._initial_performance
