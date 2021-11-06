import math

import pytest

from Nodes import MedicineCreator
from tests.testHelpers import createEngineFromConfig


def setupForIdealState(config_file):
    engine = createEngineFromConfig(config_file)

    medicine_creator = engine.getNodeById("medicine_creator")
    engine._default_outside_temperature = medicine_creator._optimal_temperature
    # Ensure that all nodes are at the perfect temperature
    for node in engine.getAllNodes().values():
        node._temperature = medicine_creator._optimal_temperature
        node.outside_temp = medicine_creator._optimal_temperature
        node.ensureSaneValues()
    return engine


@pytest.mark.parametrize("performance", [1])
@pytest.mark.parametrize("sub_ticks", [1])
@pytest.mark.parametrize('ticks', [1])
@pytest.mark.parametrize("config_file, medicine_created_per_tick", [("MedicineCreator.json", 5)])
def test_medicineProduced(config_file, medicine_created_per_tick, sub_ticks, ticks, performance):
    engine = setupForIdealState(config_file)
    engine._sub_ticks = sub_ticks
    medicine_creator = engine.getNodeById("medicine_creator")

    medicine_creator._min_performance = performance
    medicine_creator._max_performance = performance

    medicine_creator._setPerformance(performance)
    medicine_creator.target_performance = performance
    for _ in range(ticks):
        engine.doTick()

    assert math.isclose(engine.getNodeById("medicine_storage").amount_stored,
                        medicine_created_per_tick * ticks * performance)
