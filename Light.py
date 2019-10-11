from Node import Node


class Light(Node):
    def __init__(self, name):
        super().__init__()
        self.name = name
        self.isOn = False
        self._resources_required_per_tick["energy"] = 8

    def update(self):
        pass