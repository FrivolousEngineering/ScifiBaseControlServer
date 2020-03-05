from Nodes.Modifiers.Modifier import Modifier


class OverrideDefaultSafetyControlsModifier(Modifier):
    def __init__(self, duration):
        super().__init__(factors = {"min_performance": 0.5, "max_performance": 2}, duration = duration)
        pass