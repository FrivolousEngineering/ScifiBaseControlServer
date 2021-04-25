from Nodes.Modifiers.HeatPerTurnModifier import HeatPerTurnModifier


class SmallHeatPackModifier(HeatPerTurnModifier):
    def __init__(self, duration: int) -> None:
        super().__init__(duration = duration)
        self._heat_per_tick = 750
        self._name = "Small Heat Pack"
        self._abbreviation = "SHP"

        self._description = "Apply a small chemical heating pack to add heat to a device."
