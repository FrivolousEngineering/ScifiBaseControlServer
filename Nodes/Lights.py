from Nodes.ResourceDestroyer import ResourceDestroyer


class Lights(ResourceDestroyer):
    """
    Lights simulate
    """
    def __init__(self, node_id: str, amount: float, **kwargs) -> None:
        """
        :param node_id: Unique identifier of the node
        :param amount: How much power do the lights need per tick?
        :param kwargs:
        """
        del kwargs["resource_type"]
        defaults = {}
        defaults.update(kwargs)

        super().__init__(node_id, resource_type = "energy", amount = amount, **defaults)

        self._description = "A set of lights that ensure that an area can be worked in. If not enough energy is " \
                            "provided, the lights will jump to 'backup' power mode. It's still possible to work when" \
                            "this mode is activated, but it will be with decreased efficiency. Working in poor " \
                            "lighting conditions is not recommended for longer periods of time." \
                            "It should also be noted that if too little power is provided, the power it does get " \
                            "is lost!"
