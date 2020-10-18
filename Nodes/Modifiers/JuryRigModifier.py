from Nodes.Modifiers.Modifier import Modifier


class JuryRigModifier(Modifier):
    def __init__(self, temp_health: float, duration: int) -> None:
        super().__init__(duration = duration)
        self._temp_health = temp_health

        super().__init__(modifiers={"health": self._temp_health}, duration=duration)

        self._name = "Jury Rigged"

    def _onModifierRemoved(self) -> None:
        if self._node:
            self._node.damage(2 * self._temp_health)