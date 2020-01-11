from Nodes.Node import Node


class Light(Node):
    def __init__(self, node_id: str, **kwargs) -> None:
        super().__init__(node_id)
        self.is_on = False
        self._resources_required_per_tick["energy"] = 8

    def preUpdate(self):
        super().preUpdate()
        self.is_on = False

    def update(self):
        super().update()
        if self._resources_received_this_tick["energy"] == self._resources_required_per_tick["energy"]:
            self.is_on = True
