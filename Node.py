from typing import List, TYPE_CHECKING

from Connection import Connection


class Node:
    def __init__(self):
        self._incoming_connections = []  # type: List[Connection]
        self._outgoing_connections = [] # type: List[Connection]

    def updateReservations(self):
        pass

    def preUpdate(self):
        pass

    def update(self):
        pass

    def postUpdate(self):
        for connection in self._outgoing_connections:
            connection.reset()

    def requiresReplanning(self):
        num_statisfied_reservations = len([connection for connection in self._incoming_connections if connection.isReservationStatisfied()])
        if not num_statisfied_reservations:
            return False
        else:
            return len(self._incoming_connections) != num_statisfied_reservations

    def connectWith(self, type, target):
        new_connection = Connection(origin=self, target=target, resource_type = type)
        self._outgoing_connections.append(new_connection)
        target.addConnection(new_connection)

    def addConnection(self, connection: Connection) -> None:
        self._incoming_connections.append(connection)

    def getAllIncomingConnectionsByType(self, resource_type):
        return [connection for connection in self._incoming_connections if connection.resource_type == resource_type]

    def getAllOutgoingConnectionsByType(self, resource_type):
        return [connection for connection in self._outgoing_connections if connection.resource_type == resource_type]

    def _getResourceFromAllConnections(self, resource_type, amount):
        # Note; Depending on the strategy we might do something different (eg; Equal request from all, or empty
        # the first one we find)
        # Amount is the total amount that we want from all connections
        connections = self.getAllIncomingConnectionsByType(resource_type)

        # Sort to lowest amount first first
        connections = sorted(connections, key=lambda x: x.preGetResource(amount), reverse=True)
        collected_amount = 0

        # As long as we still have connections, keep doing this.
        while len(connections):
            # Check how much we should ask for (so equally from everyone)
            amount_to_request = (amount - collected_amount) / len(connections)
            # Last item of the list is the lowest one, so the one least likely to give us what we want.
            active_connection = connections.pop()
            # Check what we got.
            collected_amount += active_connection.getResource(amount_to_request)

        return collected_amount

    def reserveGetResource(self, resource_type, amount):
        pass

    def preGetResource(self, resource_type, amount) -> int:
        '''
        How much resources would this node be to give if we were to actually do it.
        :param resource_type:
        :param amount:
        :return:
        '''
        return 0

    def preGiveResource(self, resource_type, amount)-> int:
        '''
        How much resources would this node be able to accept if provideResource is called
        :param resource_type:
        :param amount:
        :return:
        '''
        return 0

    def getResource(self, resource_type, amount) -> int:
        return 0  # By default, we don't have the resource. Go home.

    def giveResource(self, resource_type, amount) -> int:
        return 0