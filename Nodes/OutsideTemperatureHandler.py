import random


class OutsideTemperatureHandler:
    """
    Randomly vary the outside temperature a tiny bit (between -1 and 1 degree)
    """
    def __init__(self) -> None:
        self._temperature = 293.15

    def getTemperatureForTick(self, tick_number: int) -> float:
        random.seed(tick_number)
        change = random.randint(-100, 100) / 100
        self._temperature += change
        return self._temperature
