from typing import Optional, TYPE_CHECKING, Dict

if TYPE_CHECKING:
    from Node import Node


class Modifier:
    def __init__(self, modifiers: Optional[Dict[str, float]] = None, factors:  Optional[Dict[str, float]] = None,
                 duration: int = 0) -> None:
        """

        :param duration: The duration this modifier will active, measured in ticks.
        """
        self._node = None  # type: Optional["Node"]

        self._duration = duration

        self._modifiers = {}
        if modifiers is not None:
            self._modifiers = modifiers

        self._factors = {}
        if factors is not None:
            self._factors = factors

    def setNode(self, node: "Node") -> None:
        self._node = node

    def getNode(self) -> Optional["Node"]:
        return self._node

    def getModifierForProperty(self, property: str) -> float:
        return self._modifiers.get(property, 0.)

    def getFactorForProperty(self, property: str):
        return self._factors.get(property, 1)

    def update(self) -> None:
        self._duration -= 1
        if self._duration <= 0 and self._node is not None:
            self._node.removeModifier(self)
            self._onModifierRemoved()

    def _onModifierRemoved(self) -> None:
        pass
