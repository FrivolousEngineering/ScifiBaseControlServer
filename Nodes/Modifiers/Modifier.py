from typing import Optional
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from Node import Node


class Modifier:
    def __init__(self, attribute: str, value: float, duration: int) -> None:
        """

        :param duration: The duration this modifier will active, measured in ticks.
        """
        self._node = None  # type: Optional["Node"]

        self._duration = duration

        self.attribute = attribute
        self.value = value

    def setNode(self, node: "Node") -> None:
        self._node = node

    def getNode(self) -> Optional["Node"]:
        return self._node

    def update(self) -> None:
        self._duration -= 1
        if self._duration <= 0 and self._node is not None:
            self._node.removeModifier(self)
            self._onModifierRemoved()

    def _onModifierRemoved(self) -> None:
        pass
