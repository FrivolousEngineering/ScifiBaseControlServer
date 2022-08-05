from typing import Dict, Optional

from Server.HardwareController import HardwareController
import dbus
import dbus.exceptions


class HardwareControllerManager:
    """
    There can be multiple external pieces of hardware that report sensor values to us. The HWCManager keeps track of
    these and the mapping of these values. This allows for sensors to directly control / set properties of Nodes
    """
    __instance = None

    def __init__(self) -> None:
        """

        """
        self._controllers = {}  # type: Dict[str, HardwareController]

        self._mapping = {"Base-Control-C64AF4": {"sensor_value": "e_to_h_valve"},
                         "Base-Control-5F7023": {"sensor_value": "h_to_g_valve"},
                         "Base-Control-941965": {"sensor_value": "h_to_e_valve"},
                         "Base-Control-5F70D9": {"sensor_value": "g_to_h_valve"},
                         "Base-Control-942AF2": {"sensor_value": "hydroponics_uncooled_water_valve"},
                         "Base-Control-C62B7E": {"sensor_value": "hydroponics_cooled_water_valve"}}

        self._min_max_values = {
            "Base-Control-C64AF4": {"min": 0, "max": 1024},
            "Base-Control-5F7023": {"min": 0, "max": 1024},
            "Base-Control-941965": {"min": 0, "max": 1024},
            "Base-Control-5F70D9": {"min": 0, "max": 1024},
            "Base-Control-942AF2": {"min": 0, "max": 1024},
            "Base-Control-C62B7E": {"min": 0, "max": 1024}
        }

        self._bus: Optional[dbus.SessionBus] = None
        self._dbus = None

    def _initDBUS(self) -> None:
        """
        Create DBUS object.
        """
        if self._bus is None:
            try:
                self._bus = dbus.SessionBus()
            except dbus.exceptions.DBusException:
                return

        if self._dbus is None:
            try:
                self._dbus = self._bus.get_object('com.frivengi.nodes', '/com/frivengi/nodes')
            except dbus.exceptions.DBusException as exception:
                self._dbus = None

    def _setupDBUS(self) -> None:
        """
        Ensure that the DBUS is setup and handled
        :return:
        """
        self._initDBUS()
        try:
            self._dbus.checkAlive()  # type: ignore
        except dbus.exceptions.DBusException:
            self._dbus = None
            # It could be that the service was rebooted, so we should try this again.
            self._initDBUS()

    def getMappedIdFromSensor(self, controller_id: str, sensor_id: str) -> Optional[str]:
        """
        Get what sensor of a given controller is mapped to what node.
        :param controller_id: Hardware controller ID
        :param sensor_id: the sensor on the hardware controller to check
        :return: ID of the node that it's mapped to, None if it wasn't found
        """
        # Find if there is a mapping!
        sensor_mapping = self._mapping.get(controller_id)
        if sensor_mapping is None:
            return None  # No mapping!

        return sensor_mapping.get(sensor_id)

    def _onSensorValueChanged(self, controller_id: str, sensor_id: str) -> None:
        """
        Handle the changes when a value of a sensor was changed.
        :param controller_id:
        :param sensor_id:
        :return:
        """
        new_value = self._controllers[controller_id].getSensorValue(sensor_id)
        if new_value is None:
            # This really shouldn't be possible...
            print("No sensor value was found, even though a signal was emitted")
            new_value = 0

        sensor_range = self._min_max_values["controller_id"]["max"] - self._min_max_values["controller_id"]["min"]

        new_value -= self._min_max_values["controller_id"]["min"]

        new_value /= sensor_range

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

    def updateController(self, controller_id: str, data: Dict[str, float]) -> None:
        """
        :param controller_id: The Id of the controller to update
        :param data: The data as reported by hardare. The keys in the dict represent the sensor_id, the values the value
                    of that sensor.
        """
        if controller_id not in self._controllers:
            self._controllers[controller_id] = HardwareController(controller_id)
            self._controllers[controller_id].sensorValueChanged.connect(self._onSensorValueChanged)
        self._controllers[controller_id].update(data)

    def getController(self, controller_id: str) -> Optional[HardwareController]:
        """
        :param controller_id: ID of the controller to request
        :return: The hardware controller if it was found, None otherwise.
        """
        return self._controllers.get(controller_id)

    def getAllControllerIds(self):
        """
        :return: All known controller Id's
        """
        return self._controllers.keys()

    @staticmethod
    def getInstance() -> "HardwareControllerManager":
        if HardwareControllerManager.__instance is None:
            HardwareControllerManager.__instance = HardwareControllerManager()
        return HardwareControllerManager.__instance
