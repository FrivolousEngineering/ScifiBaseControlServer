from Node import Node


class Light(Node):
    def __init__(self, name):
        super().__init__()
        self.name = name
        self.isOn = False
        self._resources_required_per_tick["energy"] = 8

    def preUpdate(self):
        super().preUpdate()
        self.isOn = False

    def update(self):
        super().update()
        if self._resources_received_this_tick["energy"] == self._resources_required_per_tick["energy"]:
            self.isOn = True
