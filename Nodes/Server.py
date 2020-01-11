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

        self.register_error_handler(dbus.exceptions.DBusException, self._dbusNotRunning)

        self._nodes = None

    def _dbusNotRunning(self, exception: dbus.exceptions.DBusException) -> Response:
        self._nodes = None
        return Response(flask.json.dumps({"error": "Failed to locate DBUS service"}), status=500, mimetype="application/json")

    def _setupDBUS(self) -> None:
        """
        Create DBUS object.
        """
        if self._nodes is None:
            try:
                self._nodes = self._bus.get_object('com.frivengi.nodes', '/com/frivengi/nodes')
            except dbus.exceptions.DBusException as e:
                self._nodes = None
                raise e

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
    def listAllNodeIds(self) -> Response:
        self._setupDBUS()
        result = self._nodes.getAllNodeIds()  # type: ignore
        return Response(flask.json.dumps(result), status=200, mimetype='application/json')


if __name__ == "__main__":
    server = Server()
    server.run(debug=True)

