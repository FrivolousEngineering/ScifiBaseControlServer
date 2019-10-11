from Node import Node


class Light(Node):
    def __init__(self, name):
        super().__init__()
        self.name = name
        self.isOn = False
        self._energy_required_per_tick = 8

    def preUpdate(self):
        print("preUpdating", self.name)
        connections = self.getAllIncomingConnectionsByType("energy")
        energy_to_reserve = self._energy_required_per_tick / len(connections)
        for connection in connections:
            connection.reserveResource(energy_to_reserve)

    def update(self):
        for connection in self.getAllIncomingConnectionsByType("energy"):
            connection.getResource(connection.reserved_available_amount)

    def replanReservations(self):
        print("replanning reservations for %s" % self.name)
        connections = self.getAllIncomingConnectionsByType("energy")
        total_energy_deficiency = sum([connection.getReservationDeficiency() for connection in connections])
        num_statisfied_reservations = len([connection for connection in connections if connection.isReservationStatisfied()])
        if not num_statisfied_reservations:
            print(self.name + " could not be statisfied")
            return
        extra_energy_to_ask_per_connection = total_energy_deficiency / num_statisfied_reservations
        print("Extra energy to get per connection", extra_energy_to_ask_per_connection)
        for connection in connections:
            if not connection.isReservationStatisfied():
                # So the connection that could not meet demand needs to be locked (since we can't get more!)
                connection.lock()
            else:
                # So the connections that did give us that we want might have a bit more!
                print("New amount reserved:", connection.reserved_requested_amount + extra_energy_to_ask_per_connection)
                connection.reserveResource(connection.reserved_requested_amount + extra_energy_to_ask_per_connection)