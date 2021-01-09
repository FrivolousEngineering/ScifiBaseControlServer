from Nodes.Modifiers.Modifier import Modifier


class OverclockModifier(Modifier):
    def __init__(self, duration: int) -> None:
        super().__init__(factors = {"min_performance": 3, "max_performance": 2}, duration = duration)
        self._name = "Overclock"
        self._abbreviation = "OVC"

        self._optional_tags.append("mechanical")
        self._optional_tags.append("electronic")

        self._description = "Sometimes you just have to squeeze every last bit out of a device and damn the" \
                            " concequences. Just note that this also increases the min performance. After all; Once" \
                            " it's picking up steam, it's hard to stop."

    def _onModifierAdded(self) -> None:
        # Set performance ensures that the limits are respected.
        # Once this modifier gets added, we need to ensure that the performance is in range
        node = self._node
        if node is not None:
            node.target_performance = node.target_performance

    def _onModifierRemoved(self) -> None:
        # Set performance ensures that the limits are respected.
        # Once this modifier gets removed, we need to ensure that the performance is in range again!
        node = self._node
        if node is not None:
            node.target_performance = node.target_performance