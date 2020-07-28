from typing import cast

from Nodes.ResourceStorage import ResourceStorage
from Nodes.Valve import Valve


class FluidCooler(Valve):
    """
    A fairly simple node that has a high surface area and heat emissivity.
    It can accept a certain resource, which it cools down (because of it's large surface and heat emissivity)
    """
    def __init__(self, node_id: str, resource_type: str, fluid_per_tick: float, **kwargs) -> None:
        super().__init__(node_id, resource_type, fluid_per_tick, **kwargs)
        self._surface_area = 10
        self._heat_emissivity = 0.9
        self._heat_convection_coefficient = 100

        self._weight = 5000

        self._description = "This device pumps {resource_type} from all incomming connections and provides them to" \
                            " all of it's outgoing connections all the while cooling them down significantly.".format(resource_type=resource_type)