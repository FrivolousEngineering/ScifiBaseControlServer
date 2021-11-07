import math
from unittest.mock import patch

from Nodes import OilExtractor
from tests.testHelpers import setupForIdealState
import pytest


@pytest.mark.parametrize("performance", [1, 1.5, 0.8])
@pytest.mark.parametrize("sub_ticks", [1, 10, 30])
@pytest.mark.parametrize('ticks', [1, 10, 20])
@pytest.mark.parametrize("config_file, oil_created_per_tick", [("OilExtractor.json", 5)])
def test_oilProduced_noHeat(config_file, oil_created_per_tick, sub_ticks, ticks, performance):
    engine = setupForIdealState(config_file, "oil_extractor")
    engine._sub_ticks = sub_ticks
    oil_extractor = engine.getNodeById("oil_extractor")
    oil_extractor._min_performance = performance
    oil_extractor._max_performance = performance

    oil_extractor._setPerformance(performance)
    oil_extractor.target_performance = performance
    with patch.dict(OilExtractor.COMBUSTION_HEAT, {"fuel": 0}):  # Don't add heat from burned up fuel
        for _ in range(ticks):
            engine.doTick()

    assert math.isclose(engine.getNodeById("plant_oil_storage").amount_stored,
                        oil_created_per_tick * ticks * performance)