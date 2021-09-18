import json

from Nodes.NodeEngine import NodeEngine


def createEngineFromConfig(config_file) -> NodeEngine:
    path = "tests/configurations/" + config_file
    engine = NodeEngine()
    with open(path) as f:
        loaded_data = json.loads(f.read())
        engine.deserialize(loaded_data)
    return engine