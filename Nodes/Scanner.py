from typing import Dict

from Nodes.MultiResourceDestroyer import MultiResourceDestroyer


class Scanner(MultiResourceDestroyer):
    """
    A scanner is a specialisation of a multi resource destroyer. Mostly to give the two scanners their own type
    """

    def __init__(self, node_id: str, resources_required: Dict[str, float], **kwargs) -> None:
        """
        :param node_id: Unique identifier of the node
        :param resources_required: What resources should it user per tick?
        :param kwargs:
        """
        defaults = {}
        defaults.update(kwargs)
        super().__init__(node_id, resources_required, **defaults)

        self._description = "Scanners are devices that can be used to obtain additional information on the world" \
                            "around us. Although that these devices don't directly influence the engineering " \
                            "system, apart from requiring resources, they do influence the base as a whole. Scanners" \
                            "that don't get enough resources will still function but at a significantly diminished " \
                            "capacity. "

