from Nodes.ResourceDestroyer import ResourceDestroyer


class Lights(ResourceDestroyer):
    """
    Lights simulate
    """
    def __init__(self, node_id: str, **kwargs) -> None:
        """
        :param node_id: Unique identifier of the node
        :param amount: How much power do the lights need per tick?
        :param kwargs:
        """
        defaults = {"resource_type": "energy"}
        defaults.update(kwargs)
        super().__init__(node_id, **defaults)

        self._description = "A set of lights that ensure that an area can be worked in. If not enough energy is " \
                            "provided, the lights will jump to 'backup' power mode. It's still possible to work when" \
                            "this mode is activated, but it will be with decreased efficiency. Working in poor " \
                            "lighting conditions is not recommended for longer periods of time."
