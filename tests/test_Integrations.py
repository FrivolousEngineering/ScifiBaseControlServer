import json

from Nodes.Modifiers.OverrideDefaultSafetyControlsModifier import OverrideDefaultSafetyControlsModifier
from Nodes.NodeEngine import NodeEngine
import pytest

from Nodes.NodeStorage import NodeStorage
import os
import math

from Signal import Signal


@pytest.mark.integration
@pytest.mark.parametrize("sub_ticks", [1, 5, 10])
def test_MultiWaterCooler(sub_ticks):
    engine = NodeEngine()
    # Load a nice complex setup.
    with open("tests/configurations/MultiWaterTankConfig.json") as f:
        loaded_data = json.loads(f.read())
        engine.deserialize(loaded_data)
        engine._sub_ticks = sub_ticks  # And test it with the various sub ticks!

    starting_water = engine.getNodeById("water_tank_1").amount_stored
    starting_water += engine.getNodeById("water_tank_2").amount_stored
    starting_water += engine.getNodeById("water_tank_3").amount_stored
    starting_water += engine.getNodeById("fluid_cooler_1").amount_stored
    starting_water += engine.getNodeById("fluid_cooler_2").amount_stored

    for _ in range(0, 100):
        engine.doTick()
        total_water = engine.getNodeById("water_tank_1").amount_stored
        total_water += engine.getNodeById("water_tank_2").amount_stored
        total_water += engine.getNodeById("water_tank_3").amount_stored
        total_water += engine.getNodeById("fluid_cooler_1").amount_stored
        total_water += engine.getNodeById("fluid_cooler_2").amount_stored
        # The generator can also have some water stored. Soo yay!
        total_water += engine.getNodeById("generator")._resources_left_over["water"]
        assert math.isclose(total_water, starting_water)


#@pytest.mark.parametrize("config_file", ["MultiWaterTankConfig.json", "WaterTanksWithPumps.json", "GeneratorWaterCoolerConfiguration.json"])

#
@pytest.mark.parametrize("ticks_to_run", [5, 20, 30])
@pytest.mark.parametrize("config_file", ["MultiWaterTankConfig.json", "WaterTanksWithPumps.json", "GeneratorWaterCoolerConfiguration.json"])
def test_restoreFromFile(config_file, ticks_to_run):
    engine_with_storage = NodeEngine()
    storage = NodeStorage(engine_with_storage)
    storage.storage_name = "test_storage"

    restored_engine = NodeEngine()
    path = "tests/configurations/" + config_file
    # Load a nice complex setup.
    with open(path) as f:
        loaded_data = json.loads(f.read())
        engine_with_storage.deserialize(loaded_data)
        restored_engine.deserialize(loaded_data)

    # Add a modifier
    first_key = next(iter(engine_with_storage.getAllNodes()))
    first_node = engine_with_storage.getNodeById(first_key)
    first_node.addModifier(OverrideDefaultSafetyControlsModifier(15))
    assert first_node.getModifiers()  # ensure that it was added

    for _ in range(0, ticks_to_run):
        engine_with_storage.doTick()

    # We've now created a storage file by letting the given configuration run
    # Time to restore it!
    new_storage = NodeStorage(restored_engine)
    new_storage.storage_name = "test_storage.json"
    new_storage.restoreNodeState()

    # We need to remove the file after ourselves
    os.remove(f"{storage.storage_name}.json")
    _compareStatesBetweenEngines(restored_engine, engine_with_storage)

    # Since we don't just want to check a few values, we can employ an extra trick here. If we let *both* the new and
    # the old engine do another tick, they should result in the same values. If that fails, it means some property that
    # does affect the result was not correctly restored!
    engine_with_storage.doTick()
    restored_engine.doTick()
    _compareStatesBetweenEngines(restored_engine, engine_with_storage)

    storage.purgeAllRevisions()


def _compareStatesBetweenEngines(engine_1, engine_2):
    for node_id, restored_node in engine_1.getAllNodes().items():
        if node_id != "generator":
            continue
        original_node = engine_2.getNodeById(node_id)
        for prop in original_node.additional_properties:
            assert getattr(restored_node, prop) == getattr(original_node, prop), "NOT THE SAME"

        for prop, original_value in vars(original_node).items():
            restored_value = getattr(restored_node, prop)
            if isinstance(original_value, dict):
                for key, value in original_value.items():
                    result = math.isclose(value, restored_value[key], rel_tol = 0.01)
                    if not result:
                        print(key, value, restored_value[key])
                    assert result, f"Property {key} for {prop} didn't match"

        assert math.isclose(original_node.temperature, restored_node.temperature, rel_tol = 0.01)

        assert original_node.weight == restored_node.weight
        assert restored_node.getModifiers() == original_node.getModifiers()

    assert len(engine_1.getAllNodes()) == len(engine_2.getAllNodes())


def test_restoreFromFileWithPerformanceChanges():
    target_performance = 0.5
    ticks_to_run = 10
    engine_with_storage = NodeEngine()
    storage = NodeStorage(engine_with_storage)
    storage.storage_name = "test_storage"

    engine = NodeEngine()
    path = "tests/configurations/GeneratorWaterCoolerConfiguration.json"
    # Load a nice complex setup.
    with open(path) as f:
        loaded_data = json.loads(f.read())
        engine_with_storage.deserialize(loaded_data)
        engine.deserialize(loaded_data)

    for node_id, node in engine.getAllNodes().items():
        node.target_performance = target_performance

    for _ in range(0, ticks_to_run):
        engine_with_storage.doTick()

    # We've now created a storage file by letting the given configuration run for 10 ticks!
    # Time to restore it!
    new_storage = NodeStorage(engine)
    new_storage.storage_name = "test_storage.json"
    new_storage.restoreNodeState()

    # Since we don't just want to check a few values, we can employ an extra trick here. If we let *both* the new and
    # the old engine do another tick, they should result in the same values. If that fails, it means some property that
    # does affect the result was not correctly restored!
    engine_with_storage.doTick()
    engine.doTick()

    # We need to remove the file after ourselves
    os.remove("{storage_name}.json".format(storage_name=storage.storage_name))

    for node_id, restored_node in engine.getAllNodes().items():
        original_node = engine_with_storage.getNodeById(node_id)
        assert restored_node.temperature, original_node.temperature
        assert restored_node.additional_properties == original_node.additional_properties
        assert restored_node.performance == original_node.performance
        assert restored_node.target_performance == original_node.target_performance
        assert restored_node.getModifiers() == original_node.getModifiers()

    assert len(engine.getAllNodes()) == len(engine_with_storage.getAllNodes())

    storage.purgeAllRevisions()