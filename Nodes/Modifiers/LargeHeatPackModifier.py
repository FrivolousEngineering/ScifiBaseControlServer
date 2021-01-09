from Nodes.Modifiers.HeatPerTurnModifier import HeatPerTurnModifier


class LargeHeatPackModifier(HeatPerTurnModifier):
    def __init__(self, duration: int) -> None:
        super().__init__(duration = duration)
        self._heat_per_tick = 1500
        self._name = "Large Heat Pack"
        self._abbreviation = "LHP"

        self._description = "Apply a large chemical heating pack to add heat to a device."