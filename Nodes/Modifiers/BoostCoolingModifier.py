from Nodes.Modifiers.Modifier import Modifier


class BoostCoolingModifier(Modifier):
    def __init__(self, duration: int):
        super().__init__(factors = {"heat_emissivity": 1.5, "heat_convection_coefficient": 4}, duration = duration)
        self._name = "Boost cooling"
        self._abbreviation = "BOC"
        self._description = "Significantly increase the amount of heat that is emitted and greatly increase the amount" \
                            "of heat that is lost due to convection."