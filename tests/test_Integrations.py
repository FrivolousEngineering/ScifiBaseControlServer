import json
from Nodes.NodeEngine import NodeEngine
import pytest


@pytest.mark.integration
def test_MultiWaterCooler():
    engine = NodeEngine()
    # Load a nice complex setup.
    with open("tests/configurations/MultiWaterTankConfig.json") as f:
        loaded_data = json.loads(f.read())
        engine.registerNodesFromConfigurationData(loaded_data["nodes"])
        engine.registerConnectionsFromConfigurationData(loaded_data["connections"])

    for _ in range(0, 10):
        engine.doTick()
        total_water = engine.getNodeById("water_tank_1").amount_stored
        total_water += engine.getNodeById("water_tank_2").amount_stored
        total_water += engine.getNodeById("water_tank_3").amount_stored
        total_water += engine.getNodeById("fluid_cooler_1").amount_stored
        total_water += engine.getNodeById("fluid_cooler_2").amount_stored
        # The generator can also have some water stored. Soo yay!
        total_water += engine.getNodeById("generator").getResourceAvailableThisTick("water")
        assert total_water == 2000  # We start with 2000 water, so during all ticks, this *must* remain the same!
