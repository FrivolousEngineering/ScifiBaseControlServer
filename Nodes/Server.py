import flask
from Nodes.NodeEngine import NodeEngine


class Server(flask.Flask):
    STATIC_LOCATION = ""

    def __init__(self, node_engine: "NodeEngine", port=80, **kwargs) -> None:
        super().__init__(**kwargs)

        self._node_enngine = node_engine