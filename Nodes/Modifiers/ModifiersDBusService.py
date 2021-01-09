import dbus
import dbus.service
from typing import List, Dict, Optional, Union

from Nodes.Modifiers.ModifierFactory import ModifierFactory


class ModifiersDBusService(dbus.service.Object):
    def __init__(self, session_bus: Optional[dbus.SessionBus] = None, bus_name: Optional[dbus.service.BusName] = None) -> None:
        if session_bus is None:
            self._bus = dbus.SessionBus()
        else:
            self._bus = session_bus

        if bus_name is None:
            self._bus_name = dbus.service.BusName("com.frivengi.modifiers", self._bus)
        else:
            self._bus_name = bus_name

        self._object_path = "/com/frivengi/modifiers"
        super().__init__(
            bus_name=self._bus_name,
            object_path=self._object_path
        )

    @dbus.service.method("com.frivengi.modifiers", in_signature="s", out_signature="b")
    def test(self, somestring):
        print(somestring)
        return True

    @dbus.service.method("com.frivengi.modifiers")
    def checkAlive(self) -> None:
        """
        Yes, this serves a purpose. As the name implies, this is used to check if this service is still alive.
        It doesn't actually need to return an answer, since if the service isn't there, we get an exception.
        :return:
        """
        return