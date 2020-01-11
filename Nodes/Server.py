from typing import Optional, cast, Any, List, Dict

from flask import Flask, Response
from functools import partial
import flask
from flask import render_template


_registered_routes = {}  # type: Dict[str, Dict[str, Any]]

import dbus
import dbus.exceptions




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
    STATIC_LOCATION = ""
    
    def __init__(self, *args, **kwargs) -> None:
        if "import_name" not in kwargs:
            kwargs.setdefault('import_name', __name__)

        super().__init__(*args, **kwargs)

        # Register the routes from the decorator
        for route, config_options in _registered_routes.items():
            partial_fn = partial(config_options["func"], self)
            # We must set a name to for this partial function.
            cast(Any, partial_fn).__name__ = config_options["func"].__name__
            self.add_url_rule(route, view_func = partial_fn, methods = config_options["methods"])
        self.add_url_rule(rule="/<path:path>", view_func=self.staticHost)
        self._bus = dbus.SessionBus()

        self._nodes = None

    def _setupDBUS(self) -> bool:
        """
        This ensures that the dbus connection is setup and alive.
        :return: True if the connection is up & running, false otherwise.
        """
        if self._nodes is None:
            try:
                self._nodes = self._bus.get_object('com.frivengi.nodes', '/com/frivengi/nodes')
            except dbus.exceptions.DBusException:
                return False
        try:
            self._nodes.checkAlive()
            return True
        except dbus.exceptions.DBusException:
            self._nodes = None
            return False

    def staticHost(self, path: str) -> Any:
        """
        Used for providing files that are hosted in maintenance / admin pages
        :param path:
        :return:
        """
        return flask.send_from_directory(self.STATIC_LOCATION, path)

    @register_route("/")
    def renderStartPage(self):
        return render_template("index.html")

    @register_route("/nodes")
    def listAllNodes(self):
        if not self._setupDBUS():
            return Response(flask.json.dumps({"error": "Failed to locate DBUS service"}), status=500, mimetype="application/json")
        return Response(flask.json.dumps(self._nodes.getAllNodeIds()), status=200, mimetype='application/json')


if __name__ == "__main__":
    server = Server()
    server.run(debug=True)

