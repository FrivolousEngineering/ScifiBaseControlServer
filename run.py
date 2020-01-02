from Nodes.NodeEngine import NodeEngine
import json

engine = NodeEngine()

with open("configuration.json") as f:
    loaded_data = json.loads(f.read())
    engine.registerNodesFromConfigurationData(loaded_data["nodes"])
    engine.registerConnectionsFromConfigurationData(loaded_data["connections"])

engine.doTick()

print("done")
