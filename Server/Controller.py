import time
from Signal import signalemitter, Signal


@signalemitter
class Controller:
    sensorValueChanged = Signal()

    def __init__(self, controller_id):
        self._id = controller_id
        self._sensors_values = {}

        self.time_last_seen = time.time()

    def getSensorValue(self, sensor_id):
        return self._sensors_values.get(sensor_id)

    def getAllSensorNames(self):
        return self._sensors_values.keys()

    @property
    def time_since_last_update(self):
        return time.time() - self.time_last_seen

    def update(self, data):
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