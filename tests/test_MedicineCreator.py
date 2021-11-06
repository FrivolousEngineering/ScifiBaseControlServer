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


@pytest.mark.parametrize("config_file", ["MedicineCreator.json"])
def test_temperatureIncrease(config_file):
    engine = setupForIdealState(config_file)
    temp_before = engine.getNodeById("medicine_creator").temperature
    engine.doTick()
    temp_after = engine.getNodeById("medicine_creator").temperature
    # Resources were produced, so temperature should be higher!
    assert temp_before < temp_after

    engine = setupForIdealState(config_file)
    engine.getNodeById("medicine_creator")._heat_per_medicine_created = engine.getNodeById("medicine_creator")._heat_per_medicine_created * 10
    engine.doTick()
    # Since we told it to create more heat per medicine, it should be higher
    assert temp_after < engine.getNodeById("medicine_creator").temperature


@pytest.mark.parametrize("performance", [1, 1.5, 0.8])
@pytest.mark.parametrize("sub_ticks", [1, 10, 30])
@pytest.mark.parametrize('ticks', [1, 10, 20])
@pytest.mark.parametrize("config_file, medicine_created_per_tick", [("MedicineCreator.json", 5)])
def test_medicineProduced_noHeat(config_file, medicine_created_per_tick, sub_ticks, ticks, performance):
    engine = setupForIdealState(config_file)
    engine._sub_ticks = sub_ticks
    medicine_creator = engine.getNodeById("medicine_creator")
    medicine_creator._heat_per_medicine_created = 0
    medicine_creator._min_performance = performance
    medicine_creator._max_performance = performance

    medicine_creator._setPerformance(performance)
    medicine_creator.target_performance = performance
    for _ in range(ticks):
        engine.doTick()

    assert math.isclose(engine.getNodeById("medicine_storage").amount_stored,
                        medicine_created_per_tick * ticks * performance)
