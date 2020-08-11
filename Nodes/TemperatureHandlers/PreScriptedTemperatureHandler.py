
from .TemperatureHandler import TemperatureHandler
from Nodes.Constants import SECONDS_PER_TICK


class PreScriptedTemperatureHandler(TemperatureHandler):
    def __init__(self) -> None:
        self._temperature = 293.15

        # Hardcoded the temperatures of today. It was fucking hot :(
        self._temperatures_per_hour = [297.2, 296.2, 295.2, 294.8, 294.5, 294.2, 294.8, 295.5, 296.2, 297.8, 299.5, 301.2, 302.5, 303.8, 305.2, 305.2, 305.2, 305.2, 304.2, 303.2, 302.2, 300.5, 298.8, 297.2]

    def getTemperatureForTick(self, tick_number: int) -> float:
        # Every tick is 30 seconds. So first we calculate that back to a time.
        # Assume that we start at 00:00 (middle of the night).

        time_in_seconds = tick_number * SECONDS_PER_TICK

        # Ensure that the time is cut off per day
        while time_in_seconds >= 86400:
            time_in_seconds -= 86400

        hour = int(time_in_seconds / 3600)
        time_left = time_in_seconds - hour * 3600
        minute = int(time_left / 60)

        hour_value = self._temperatures_per_hour[hour]
        if hour == 23:
            next_hour_value = self._temperatures_per_hour[0]
        else:
            next_hour_value = self._temperatures_per_hour[hour + 1]

        temp_difference_per_minute = (next_hour_value - hour_value) / 60
        return hour_value + temp_difference_per_minute *  minute
