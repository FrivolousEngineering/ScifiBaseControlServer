from Nodes.Generator import Generator
from Nodes.NodeEngine import NodeEngine
from Nodes.NodeGraph import NodeGraph
from Nodes.ResourceStorage import ResourceStorage
from Nodes.FluidCooler import FluidCooler
import json

engine = NodeEngine()

with open("configuration.json") as f:
    loaded_data = json.loads(f.read())
    engine.registerNodesFromSerialized(loaded_data["nodes"])
    engine.registerConnectionsFromSerialized(loaded_data["connections"])

print("done")

