import time
from typing import Optional, List, Dict

from Signal import signalemitter, Signal


@signalemitter
class HardwareController:
    """
    A convenience object that keeps track of data that we got from a single (external!) piece of hardware.
    It tracks the sensor values that it got from it, as well as the version and the time it last reported something.
    """
    sensorValueChanged = Signal()

    def __init__(self, controller_id: str) -> None:
        """
        Create hardware controller with a given ID
        :param controller_id: The id of the unit
        """
        self._id = controller_id
        self._sensors_values: Dict[str, Optional[float]] = {}

        # Since the controllers are remote devices, it could be that they have different versions.
        self.version_string = "Unknown"

        self.time_last_seen = time.time()

    def getSensorValue(self, sensor_id: str) -> Optional[float]:
        """
        Get the last reported value of a sensor of this hardware.
        :param sensor_id: Sensor id to get the value of
        :return: the value, None if it doesn't have data or the sensor doesn't exist
        """
        return self._sensors_values.get(sensor_id)

    def getAllSensorNames(self) -> List[str]:
        """
        A single piece of hardware can have multiple sensors. This provides a list of the name sof these sensors.
        :return:
        """
        return list(self._sensors_values.keys())

    @property
    def time_since_last_update(self):
        return time.time() - self.time_last_seen

    def update(self, data: Dict[str, float]) -> None:
        """
        Update the stored data of the controller
        :param data: The data as reported by the external hardware.
        :return:
        """
        self.time_last_seen = time.time()
        changed_sensors = []
        # First do all the updates.
        for key in data:
            if key not in self._sensors_values:
                self._sensors_values[key] = None

            if self._sensors_values[key] != data[key]:
                self._sensors_values[key] = data[key]
                changed_sensors.append(key)

        # Then notify everyone!
        for key in changed_sensors:
            self.sensorValueChanged.emit(self._id, key)
