from Nodes.NodeEngine import NodeEngine
import json

from Nodes.NodeStorage import NodeStorage

engine = NodeEngine()

with open("configuration.json") as f:
    loaded_data = json.loads(f.read())
    engine.registerNodesFromConfigurationData(loaded_data["nodes"])
    engine.registerConnectionsFromConfigurationData(loaded_data["connections"])


storage = NodeStorage(engine)

engine.doTick()
engine.doTick()
engine.doTick()

print("done")
