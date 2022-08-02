from Nodes.Modifiers.HeatPerTurnModifier import HeatPerTurnModifier


class MediumHeatPackModifier(HeatPerTurnModifier):
    def __init__(self, duration: int) -> None:
        super().__init__(duration = duration)
        self._heat_per_tick = 225000
        self._name = "Medium Heat Pack"
        self._abbreviation = "MHP"

        self._description = "Apply a medium chemical heating pack to add heat to a device."
        self._required_engineering_level = 2
