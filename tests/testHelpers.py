import json

from Nodes.NodeEngine import NodeEngine
from Nodes.NodeStorage import NodeStorage


def createEngineFromConfig(config_file):
    path = "tests/configurations/" + config_file
    engine = NodeEngine()
    with open(path) as f:
        loaded_data = json.loads(f.read())
        engine.deserialize(loaded_data)
    return engine