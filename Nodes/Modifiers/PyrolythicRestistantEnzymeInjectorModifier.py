from Nodes.Modifiers.Modifier import Modifier


class PyrolythicResistantEnzymeInjectorModifier(Modifier):
    def __init__(self, duration: int) -> None:
        super().__init__(factors = {"optimal_temperature_range": 1.5}, modifiers = {"optimal_temperature": -10}, duration = duration)

        self._name = "Pyrolythic Resistant Enzyme Injector"
        self._abbreviation = "PEI"

        self._required_tag = "plant"

        self._description = "Plants are fickle, but in the end they are just tiny little machines. Regulations say" \
                            " that these enzymes shouldn't be used non stop. No-one really knows why. Using them " \
                            " will make the plants grow better at a lower temperature and it also increases the range" \
                            " in which they are comfortable."
