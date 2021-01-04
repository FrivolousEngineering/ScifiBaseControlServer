from Nodes.Modifiers.Modifier import Modifier


class OverrideDefaultSafetyControlsModifier(Modifier):
    def __init__(self, duration: int) -> None:
        super().__init__(factors = {"min_performance": 0.5, "max_performance": 2}, duration = duration)
        self._name = "Override Default Safety"
        self._abbreviation = "ODS"

    def _onModifierRemoved(self) -> None:
        # Set performance ensures that the limits are respected.
        # Once this modifier gets removed, we need to ensure that the performance is in range again!
        node = self._node
        if node is not None:
            node.target_performance = node.target_performance