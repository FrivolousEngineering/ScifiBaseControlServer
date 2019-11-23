from typing import Optional, cast, Any, List, Dict

from flask import Flask, Response
from functools import partial
import flask

from Nodes.Node import Node
from Nodes.NodeEngine import NodeEngine

_registered_routes = {}  # type: Dict[str, Dict[str, Any]]


def register_route(route: Optional[str] = None, accepted_methods: Optional[List[str]] = None):
    # simple decorator for class based views
    def inner(fn):
        result_dict = {"func": fn}
        if accepted_methods is None:
            result_dict["methods"] = ["GET"]
        else:
            result_dict["methods"] = accepted_methods
        _registered_routes[route] = result_dict
        return fn
    return inner


class Server(Flask):
    def __init__(self, *args, **kwargs) -> None:
        if "import_name" not in kwargs:
            kwargs.setdefault('import_name', __name__)
        super().__init__(*args, **kwargs)

        # Register the routes from the decorator
        for route, config_options in _registered_routes.items():
            partial_fn = partial(config_options["func"], self)
            endpoint = cast(Any, partial_fn).__name__ = config_options["func"].__name__
            self.add_url_rule(route, view_func = partial_fn, methods = config_options["methods"])

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

