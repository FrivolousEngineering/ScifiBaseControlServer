from Nodes.Modifiers.Modifier import Modifier


class RepairOverTimeModifier(Modifier):
    def __init__(self, amount_to_repair_per_turn: float, duration: int) -> None:
        super().__init__(duration = duration)
        self._amount_to_repair_per_turn = amount_to_repair_per_turn
        self._name = "Careful Repair"
        self._abbreviation = "ROT"

        self._description = "Slowly repair a device without impacting it's operation."

    def update(self) -> None:
        super().update()

        node = self._node
        if node is not None:
            node.repair(self._amount_to_repair_per_turn)