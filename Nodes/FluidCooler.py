from typing import cast

from Nodes.ResourceStorage import ResourceStorage
from Nodes.Valve import Valve


class FluidCooler(Valve):
    """
    A fairly simple node that has a high surface area and heat emissivity.
    It can accept a certain resource, which it cools down (because of it's large surface and heat emissivity)
    """
    def __init__(self, node_id: str, resource_type: str, fluid_per_tick: float, **kwargs) -> None:
        # Update the defaults like this so that the actual property can be set by base class
        defaults = {"weight": 5000,
                    "surface_area": 10,
                    "heat_emissivity": 0.9,
                    "heat_convection_coefficient": 100}
        defaults.update(kwargs)
        super().__init__(node_id, resource_type, fluid_per_tick, **defaults)

        self._description = "This device pumps {resource_type} from all incomming connections and provides them to" \
                            " all of it's outgoing connections all the while cooling them down significantly."
        self._description = self._description.format(resource_type=resource_type)