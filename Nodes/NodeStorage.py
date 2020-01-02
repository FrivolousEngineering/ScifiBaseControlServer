from typing import TYPE_CHECKING, List, Dict, Any
from atomicwrites import atomic_write

import json

if TYPE_CHECKING:
    from Nodes.NodeEngine import NodeEngine


class NodeStorage:
    def __init__(self, engine: "NodeEngine") -> None:
        self._engine = engine

    def serializeAllNodes(self) -> List[Dict[str, Any]]:
        data = []
        for node in self._engine.getAllNodes().values():
            data.append(node.serialize())
        return data

    def storeNodeState(self) -> None:
        data_to_write = self.serializeAllNodes()

        with atomic_write("node_state.json", overwrite=True) as f:
            # TODO: This always overrides, which isn't that safe. Might want to think about a somewhat smarter solution
            # that keeps a number of previous states (so if one fails it can still recover an older one)
            f.write(json.dumps(data_to_write, separators=(", ", ": "), indent=4))

    def restoreNodeState(self) -> None:
        with open("node_state.json") as f:
            data = f.read()

        parsed_json = json.loads(data)
        for entry in parsed_json:
            # TODO: This has no fault handling what so ever, which should be added at some point.
            node = self._engine.getNodeById(entry["node_id"])
            node.deserialize(entry)