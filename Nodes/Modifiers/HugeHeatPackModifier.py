from Nodes.Modifiers.HeatPerTurnModifier import HeatPerTurnModifier


class HugeHeatPackModifier(HeatPerTurnModifier):
    def __init__(self, duration: int) -> None:
        super().__init__(duration = duration)
        self._heat_per_tick = 900000
        self._name = "Huge Heat Pack"
        self._abbreviation = "HHP"

        self._description = "Apply a huge chemical heating pack to add heat to a device. Using this will cause some " \
                            "damage on the system."
        self._required_engineering_level = 5

    def update(self) -> None:
        super().update()

        node = self._node
        if node is not None:
            node.damage(0.5)