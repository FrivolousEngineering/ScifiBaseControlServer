
import dbus
import dbus.service

from Nodes.NodeEngine import NodeEngine


class DBusService(dbus.service.Object):
    def __init__(self, engine: NodeEngine) -> None:
        self._bus = dbus.SessionBus()
        super().__init__(
            bus_name = dbus.service.BusName("com.frivengi.nodes", self._bus),
            object_path = "/com/frivengi/nodes"
        )

        self._node_engine = engine

    @dbus.service.method("com.frivengi.nodes", out_signature="s", in_signature = "s")
    def getNodeInfo(self, node_id: str) -> str:
        return str(self._node_engine.getNodeById(node_id))

