import json

from Nodes.NodeEngine import NodeEngine


def createEngineFromConfig(config_file) -> NodeEngine:
    path = "tests/configurations/" + config_file
    engine = NodeEngine()
    with open(path) as f:
        loaded_data = json.loads(f.read())
        engine.deserialize(loaded_data)
    return engine


def setupForIdealState(config_file, target_node_id):
    engine = createEngineFromConfig(config_file)

    target_node = engine.getNodeById(target_node_id)
    engine._default_outside_temperature = target_node._optimal_temperature
    # Ensure that all nodes are at the perfect temperature
    for node in engine.getAllNodes().values():
        node._temperature = target_node._optimal_temperature
        node.outside_temp = target_node._optimal_temperature
        node.ensureSaneValues()
    return engine