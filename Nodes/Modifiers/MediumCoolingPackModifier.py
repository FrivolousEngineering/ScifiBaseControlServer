from Nodes.Modifiers.HeatPerTurnModifier import HeatPerTurnModifier


class MediumCoolingPackModifier(HeatPerTurnModifier):
    def __init__(self, duration: int) -> None:
        super().__init__(duration = duration)
        self._heat_per_tick = -750
        self._name = "Medium Cooling Pack"
        self._abbreviation = "MCP"
        self._description = "Apply a medium chemical cooling pack to extract heat from a device."