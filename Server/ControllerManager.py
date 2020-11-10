from typing import Dict, Optional

from Server.Controller import Controller


class ControllerManager:

    __instance = None

    def __init__(self):
        self._controllers = {}  # type: Dict[str, Controller]

    def _onSensorValueChanged(self, controller_id, sensor_id):
        new_value = self._controllers[controller_id].getSensorValue(sensor_id)

        # Todo: Implement the mapping
        print("SENSOR CHANGED", controller_id, sensor_id, new_value)

    def updateController(self, controller_id, data):
        if controller_id not in self._controllers:
            self._controllers[controller_id] = Controller(controller_id)
            self._controllers[controller_id].sensorValueChanged.connect(self._onSensorValueChanged)
        self._controllers[controller_id].update(data)

    def getController(self, controller_id) -> Optional[Controller]:
        return self._controllers.get(controller_id)

    @staticmethod
    def getInstance() -> "ControllerManager":
        if ControllerManager.__instance is None:
            ControllerManager.__instance = ControllerManager()
        return ControllerManager.__instance
