from Nodes.Modifiers.Modifier import Modifier


class OverrideDefaultSafetyControlsModifier(Modifier):
    def __init__(self, duration):
        super().__init__(factors = {"min_performance": 0.5, "max_performance": 2}, duration = duration)

    def _onModifierRemoved(self) -> None:
        # Set performance ensures that the limits are respected.
        # Once this modifier gets removed, we need to ensure that the performance is in range again!
        node = self._node
        if node is not None:
            node.performance = node.performance