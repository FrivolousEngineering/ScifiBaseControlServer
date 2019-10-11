from Node import Node


class Generator(Node):
    def __init__(self):
        super().__init__()

    def update(self):
        # So a generator will attempt to get sum resources!
        # Hardcoded to require 10 fuel and produce 10 Energy

        # Attempt to gather resources!
        amount_fuel_available = 0
        for connection in self.getAllIncomingConnectionsByType("fuel"):
            # We found the right one, yay!
            fuel_still_required = 20 - amount_fuel_available

            fuel_from_connection = connection.getResource(fuel_still_required)

            amount_fuel_available += fuel_from_connection
            if amount_fuel_available == 20:
                break

        print("Managed to get %s fuel" % amount_fuel_available)

        for connection in self.getAllOutgoingConnectionsByType("energy"):
            connection.giveResource(amount_fuel_available)
