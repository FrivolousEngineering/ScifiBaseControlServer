import math

import pytest

from tests.testHelpers import createEngineFromConfig


@pytest.mark.parametrize("sub_ticks", [1, 10, 30])
@pytest.mark.parametrize("config_file", ["PlantPress.json"])
def test_sameTemperature(config_file, sub_ticks):
    # The plant press doesn't generate any heat, so check if running it for one tick ensures that the temp is the same
    engine = createEngineFromConfig(config_file)
    engine._sub_ticks = sub_ticks
    plant_press = engine.getNodeById("plant_press")
    begin_temp = plant_press.temperature
    engine.doTick()
    assert math.isclose(plant_press.temperature, begin_temp)


