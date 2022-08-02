from Nodes.Modifiers.HeatPerTurnModifier import HeatPerTurnModifier


class LargeCoolingPackModifier(HeatPerTurnModifier):
    def __init__(self, duration: int) -> None:
        super().__init__(duration = duration)
        self._heat_per_tick = -450000
        self._name = "Large Cooling Pack"
        self._abbreviation = "LCP"

        self._description = "Apply a large chemical cooling pack to extract heat from a device."
        self._required_engineering_level = 3