import math

import pytest

from tests.testHelpers import setupForIdealState


@pytest.mark.parametrize("config_file", ["MedicineCreator.json"])
def test_temperatureIncrease(config_file):
    engine = setupForIdealState(config_file, "medicine_creator")
    temp_before = engine.getNodeById("medicine_creator").temperature
    engine.doTick()
    temp_after = engine.getNodeById("medicine_creator").temperature
    # Resources were produced, so temperature should be higher!
    assert temp_before < temp_after

    engine = setupForIdealState(config_file, "medicine_creator")
    engine.getNodeById("medicine_creator")._heat_per_medicine_created = engine.getNodeById("medicine_creator")._heat_per_medicine_created * 10
    engine.doTick()
    # Since we told it to create more heat per medicine, it should be higher
    assert temp_after < engine.getNodeById("medicine_creator").temperature


@pytest.mark.parametrize("performance", [1, 1.5, 0.8])
@pytest.mark.parametrize("sub_ticks", [1, 10, 30])
@pytest.mark.parametrize('ticks', [1, 10, 20])
@pytest.mark.parametrize("config_file, medicine_created_per_tick", [("MedicineCreator.json", 5)])
def test_medicineProduced_noHeat(config_file, medicine_created_per_tick, sub_ticks, ticks, performance):
    engine = setupForIdealState(config_file, "medicine_creator")
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
