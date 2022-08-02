from Nodes.Modifiers.HeatPerTurnModifier import HeatPerTurnModifier


class SmallCoolingPackModifier(HeatPerTurnModifier):
    def __init__(self, duration: int) -> None:
        super().__init__(duration = duration)
        self._heat_per_tick = -112500
        self._name = "Small Cooling Pack"
        self._abbreviation = "SCP"

        self._description = "Apply a small chemical cooling pack to extract heat from a device."
