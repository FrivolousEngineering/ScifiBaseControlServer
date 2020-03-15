import json

from Nodes.Modifiers.OverrideDefaultSafetyControlsModifier import OverrideDefaultSafetyControlsModifier
from Nodes.NodeEngine import NodeEngine
import pytest

from Nodes.NodeStorage import NodeStorage


@pytest.mark.integration
def test_MultiWaterCooler():
    engine = NodeEngine()
    # Load a nice complex setup.
    with open("tests/configurations/MultiWaterTankConfig.json") as f:
        loaded_data = json.loads(f.read())
        engine.registerNodesFromConfigurationData(loaded_data["nodes"])
        engine.registerConnectionsFromConfigurationData(loaded_data["connections"])

    for _ in range(0, 200):
        engine.doTick()
        total_water = engine.getNodeById("water_tank_1").amount_stored
        total_water += engine.getNodeById("water_tank_2").amount_stored
        total_water += engine.getNodeById("water_tank_3").amount_stored
        total_water += engine.getNodeById("fluid_cooler_1").amount_stored
        total_water += engine.getNodeById("fluid_cooler_2").amount_stored
        # The generator can also have some water stored. Soo yay!
        total_water += engine.getNodeById("generator").getResourceAvailableThisTick("water")
        assert total_water == 2000  # We start with 2000 water, so during all ticks, this *must* remain the same!


def test_restoreFromFile():
    engine_with_storage = NodeEngine()
    storage = NodeStorage(engine_with_storage)

    engine = NodeEngine()

    # Load a nice complex setup.
    with open("tests/configurations/MultiWaterTankConfig.json") as f:
        loaded_data = json.loads(f.read())
        engine_with_storage.registerNodesFromConfigurationData(loaded_data["nodes"])
        engine_with_storage.registerConnectionsFromConfigurationData(loaded_data["connections"])

        engine.registerNodesFromConfigurationData(loaded_data["nodes"])
        engine.registerConnectionsFromConfigurationData(loaded_data["connections"])

    # Add a modifier
    first_key = next(iter(engine_with_storage.getAllNodes()))
    first_node = engine_with_storage.getNodeById(first_key)
    first_node.addModifier(OverrideDefaultSafetyControlsModifier(5))

    for _ in range(0, 10):
        engine_with_storage.doTick()

    # We've now created a storage file by letting the given configuration run for 10 ticks!
    # Time to restore it!
    new_storage = NodeStorage(engine)
    new_storage.restoreNodeState()

    for node_id, restored_node in engine.getAllNodes().items():
        original_node = engine_with_storage.getNodeById(node_id)
        assert restored_node.temperature, original_node.temperature
        assert restored_node.additional_properties == original_node.additional_properties
        assert restored_node.getModifiers() == original_node.getModifiers()

    assert len(engine.getAllNodes()) == len(engine_with_storage.getAllNodes())