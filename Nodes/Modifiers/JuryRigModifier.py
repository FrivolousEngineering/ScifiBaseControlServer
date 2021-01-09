from Nodes.Modifiers.Modifier import Modifier


class JuryRigModifier(Modifier):
    def __init__(self, temp_health: float, duration: int) -> None:
        super().__init__(duration = duration)
        self._temp_health = temp_health

        super().__init__(modifiers={"health": self._temp_health}, duration=duration)

        self._name = "Jury Rigging"

        self._description = "This is a last ditch attempt to fix a machine. It will work for a bit longer, but once the" \
                            "temporary fixes give out, it's bound to break all kinds of expensive things."

    def _onModifierRemoved(self) -> None:
        if self._node:
            self._node.damage(2 * self._temp_health)