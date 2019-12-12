from Nodes.NodeEngine import NodeEngine
import json

engine = NodeEngine()

with open("configuration.json") as f:
    loaded_data = json.loads(f.read())
    engine.registerNodesFromSerialized(loaded_data["nodes"])
    engine.registerConnectionsFromSerialized(loaded_data["connections"])

print("done")

