from typing import Optional, cast, Any

from flask import Flask, Response
from functools import partial
import flask

from Nodes.Node import Node
from Nodes.NodeEngine import NodeEngine

_registered_routes = {}


def register_route(route: Optional[str]= None):
    # simple decorator for class based views
    def inner(fn):
        _registered_routes[route] = fn
        return fn
    return inner


class Server(Flask):
    def __init__(self, *args, **kwargs) -> None:
        if "import_name" not in kwargs:
            kwargs.setdefault('import_name', __name__)
        super().__init__(*args, **kwargs)
        # register the routes from the decorator
        for route, fn in _registered_routes.items():
            partial_fn = partial(fn, self)
            cast(Any, partial_fn).__name__ = fn.__name__
            self.route(route)(partial_fn)

        self._node_engine = None # type: Optional[NodeEngine]

    def setEngine(self, node_engine: NodeEngine) -> None:
        self._node_engine = node_engine

    @register_route("/")
    def listAllNodes(self):
        if self._node_engine is None:
            return ""

        return Response(flask.json.dumps(self._node_engine.getAllNodeIds()), status=200, mimetype='application/json')


if __name__ == "__main__":
    server = Server()
    engine = NodeEngine()

    engine.registerNode(Node("ZOMG"))
    server.setEngine(engine)
    server.run(debug=True)

    # TEST CODE;

