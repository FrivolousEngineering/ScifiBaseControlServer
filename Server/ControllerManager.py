from typing import Dict, Optional

from Server.Controller import Controller
import dbus
import dbus.exceptions


class ControllerManager:
    __instance = None

    def __init__(self) -> None:
        self._controllers = {}  # type: Dict[str, Controller]

        self._mapping = {"Base-Control-C64AF4": {"sensor_value": "generator"}}
        self._bus = dbus.SessionBus()
        self._dbus = None

    def _initDBUS(self) -> None:
        """
        Create DBUS object.
        """
        if self._dbus is None:
            try:
                self._dbus = self._bus.get_object('com.frivengi.nodes', '/com/frivengi/nodes')
            except dbus.exceptions.DBusException as exception:
                self._dbus = None

    def _setupDBUS(self) -> None:
        self._initDBUS()
        try:
            self._dbus.checkAlive()  # type: ignore
        except dbus.exceptions.DBusException:
            self._dbus = None
            # It could be that the service was rebooted, so we should try this again.
            self._initDBUS()

    def getMappedIdFromSensor(self, controller_id: str, sensor_id: str) -> Optional[str]:
        # Find if there is a mapping!
        sensor_mapping = self._mapping.get(controller_id)
        if sensor_mapping is None:
            return None # No mapping!

        return sensor_mapping.get(sensor_id)

    def _onSensorValueChanged(self, controller_id, sensor_id):
        new_value = self._controllers[controller_id].getSensorValue(sensor_id)
        new_value /= 1024.

        node_id = self.getMappedIdFromSensor(controller_id, sensor_id)
        if node_id is None:
            return

        self._setupDBUS()
        if self._dbus is None:
            print("Couldn't create dbus")
            # Couldn't make the changes.
            # We should probably store this somewhere so we can try later...
            return
        if not self._dbus.doesNodeExist(node_id):
            print("Node doesn't exist", node_id)
            # Node doesn't exist. Something went wrong here :(
            return

        # For the moment we only support setting the target performance.
        self._dbus.setTargetPerformance(node_id, float(new_value))

    def updateController(self, controller_id, data):
        if controller_id not in self._controllers:
            self._controllers[controller_id] = Controller(controller_id)
            self._controllers[controller_id].sensorValueChanged.connect(self._onSensorValueChanged)
        self._controllers[controller_id].update(data)

    def getController(self, controller_id) -> Optional[Controller]:
        return self._controllers.get(controller_id)

    def getAllControllerIds(self):
        return self._controllers.keys()

    @staticmethod
    def getInstance() -> "ControllerManager":
        if ControllerManager.__instance is None:
            ControllerManager.__instance = ControllerManager()
        return ControllerManager.__instance
