from Nodes.Modifiers.Modifier import Modifier


class HeatPerTurnModifier(Modifier):
    """
    Abstract modifier (used for the various cooling & heating modifiers!)
    """
    def __init__(self, duration: int) -> None:
        super().__init__(duration = duration)
        self._heat_per_tick = 0

    def update(self) -> None:
        super().update()

        node = self._node
        if node is not None:
            node.addHeat(self._heat_per_tick)