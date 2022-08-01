from Nodes.ResourceDestroyer import ResourceDestroyer


class SoundSystem(ResourceDestroyer):
    """
    A sound system
    """
    def __init__(self, node_id: str, amount: float, **kwargs) -> None:
        """
        :param node_id: Unique identifier of the node
        :param amount: How much power does the sound system need per tick?
        :param kwargs:
        """
        if "resource_type" in kwargs:
            del kwargs["resource_type"]
        defaults = {}
        defaults.update(kwargs)

        super().__init__(node_id, resource_type = "energy", amount = amount, **defaults)

        self._description = "A system that can play sound. It can be music, an alarm, or information."
