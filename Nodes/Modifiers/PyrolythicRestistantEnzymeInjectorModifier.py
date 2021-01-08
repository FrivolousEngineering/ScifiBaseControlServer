

from Nodes.Modifiers.Modifier import Modifier


class PyrolythicResistantEnzymeInjectorModifier(Modifier):
    def __init__(self, duration: int) -> None:
        super().__init__(factors = {"optimal_temperature_range": 1.5}, modifiers = {"optimal_temperature": -10}, duration = duration)

        self._name = "Pyrolythic Resistant Enzyme Injector"
        self._abbreviation = "PEI"

        self._required_tag = "plant"
