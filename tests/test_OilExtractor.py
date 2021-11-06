import math

from tests.testHelpers import createEngineFromConfig
import pytest


def setupForIdealState(config_file):
    engine = createEngineFromConfig(config_file)

    oil_extractor = engine.getNodeById("oil_extractor")
    engine._default_outside_temperature = oil_extractor._optimal_temperature
    # Ensure that all nodes are at the perfect temperature
    for node in engine.getAllNodes().values():
        node._temperature = oil_extractor._optimal_temperature
        node.outside_temp = oil_extractor._optimal_temperature
        node.ensureSaneValues()
    return engine


@pytest.mark.parametrize("performance", [1, 1.5, 0.8])
@pytest.mark.parametrize("sub_ticks", [1, 10, 30])
@pytest.mark.parametrize('ticks', [1])
@pytest.mark.parametrize("config_file, oil_created_per_tick", [("OilExtractor.json", 5)])
def test_medicineProduced(config_file, oil_created_per_tick, sub_ticks, ticks, performance):
    engine = setupForIdealState(config_file)
    engine._sub_ticks = sub_ticks
    oil_extractor = engine.getNodeById("oil_extractor")
    oil_extractor._min_performance = performance
    oil_extractor._max_performance = performance

    oil_extractor._setPerformance(performance)
    oil_extractor.target_performance = performance
    for _ in range(ticks):
        engine.doTick()

    assert math.isclose(engine.getNodeById("plant_oil_storage").amount_stored,
                        oil_created_per_tick * ticks * performance)