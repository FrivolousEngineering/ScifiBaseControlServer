from typing import Optional, cast, Any, List, Dict

from flask import Flask, Response
from functools import partial
import flask
from flask import render_template, request


_REGISTERED_ROUTES = {}  # type: Dict[str, Dict[str, Any]]

import dbus
import dbus.exceptions


def register_route(route: Optional[str] = None, accepted_methods: Optional[List[str]] = None):
    # simple decorator for class based views
    def inner(function):
        result_dict = {"func": function}
        if accepted_methods is None:
            result_dict["methods"] = ["GET"]
        else:
            result_dict["methods"] = accepted_methods
        _REGISTERED_ROUTES[route] = result_dict
        return function
    return inner


class Server(Flask):
    STATIC_LOCATION = ""
    
    def __init__(self, *args, **kwargs) -> None:
        if "import_name" not in kwargs:
            kwargs.setdefault('import_name', __name__)

        super().__init__(*args, **kwargs)

        # Register the routes from the decorator
        for route, config_options in _REGISTERED_ROUTES.items():
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
        return Response(flask.json.dumps({"error": "DBUS Exception", "message": str(exception)}),
                        status=500,
                        mimetype="application/json")

    def _setupDBUS(self) -> None:
        self._initDBUS()
        try:
            self._nodes.checkAlive()  # type: ignore
        except dbus.exceptions.DBusException:
            self._nodes = None
            # It could be that the service was rebooted, so we should try this again.
            self._initDBUS()

    def _initDBUS(self) -> None:
        """
        Create DBUS object.
        """
        if self._nodes is None:
            try:
                self._nodes = self._bus.get_object('com.frivengi.nodes', '/com/frivengi/nodes')
            except dbus.exceptions.DBusException as exception:
                self._nodes = None
                raise exception

    def staticHost(self, path: str) -> Any:
        """
        Used for providing files that are hosted in maintenance / admin pages
        :param path:
        :return:
        """
        return flask.send_from_directory(self.STATIC_LOCATION, path)

    @register_route("/")
    def renderStartPage(self):
        self._setupDBUS()
        display_data = []
        for node_id in self._nodes.getAllNodeIds():  # type: ignore
            data = {"node_id": node_id,
                    "temperature": self._nodes.getNodeTemperature(node_id),
                    "amount": self._nodes.getAmountStored(node_id),
                    "enabled": self._nodes.isNodeEnabled(node_id)} # type: ignore
            display_data.append(data)
        return render_template("index.html", data = display_data)

    def getNodeData(self, node_id: str):
        data = {"node_id": node_id,
                "temperature": self._nodes.getNodeTemperature(node_id),  # type: ignore
                "amount": round(self._nodes.getAmountStored(node_id), 2),  # type: ignore
                "enabled": self._nodes.isNodeEnabled(node_id),  # type: ignore
                "active": self._nodes.isNodeActive(node_id)}  # type: ignore
        return data

    @register_route("/<node_id>/")
    def nodeData(self, node_id: str):
        self._setupDBUS()
        data = self.getNodeData((node_id))
        return Response(flask.json.dumps(data), status = 200, mimetype="application/json")

    @register_route("/nodes/")
    def getAllNodeData(self):
        self._setupDBUS()
        display_data = []
        for node_id in self._nodes.getAllNodeIds():  # type: ignore
            data = self.getNodeData(node_id)
            display_data.append(data)
        return Response(flask.json.dumps(display_data), status=200, mimetype="application/json")

    @register_route("/nodes")
    def listAllNodeIds(self) -> Response:
        self._setupDBUS()
        result = self._nodes.getAllNodeIds()  # type: ignore
        return Response(flask.json.dumps(result), status=200, mimetype="application/json")

    @register_route("/startTick", ["POST"])
    def startTick(self) -> Response:
        self._setupDBUS()
        self._nodes.doTick()  # type: ignore

        return Response(flask.json.dumps({"message": ""}), status=200, mimetype="application/json")

    @register_route("/<node_id>/enabled/", ["PUT", "GET"])
    def nodeEnabled(self, node_id):
        self._setupDBUS()
        if request.method == "PUT":
            self._nodes.setNodeEnabled(node_id, not self._nodes.isNodeEnabled(node_id))
            return Response(flask.json.dumps({"message": ""}), status=200, mimetype="application/json")
        return Response(flask.json.dumps(self._nodes.isNodeEnabled(node_id)), status=200, mimetype="application/json")

    @register_route("/<node_id>/temperature/history/")
    def temperatureHistory(self, node_id):
        self._setupDBUS()
        result = self._nodes.getNodeTemperatureHistory(node_id)  # type: ignore
        return Response(flask.json.dumps(result), status=200, mimetype="application/json")

    @register_route("/<node_id>/temperature/")
    def temperature(self, node_id):
        self._setupDBUS()
        result = self._nodes.getNodeTemperature(node_id)  # type: ignore
        return Response(flask.json.dumps(result), status=200, mimetype="application/json")

    @register_route("/<node_id>/<prop>/history/")
    def additionalPropertyHistory(self, node_id, prop):
        self._setupDBUS()
        additional_property_history = self._nodes.getAdditionalPropertyHistory(node_id, prop)
        return Response(flask.json.dumps(additional_property_history), status=200, mimetype="application/json")

    @register_route("/<node_id>/additional_properties")
    def getAdditionalProperties(self, node_id):
        self._setupDBUS()
        result = self._nodes.getAdditionalProperties(node_id)
        return Response(flask.json.dumps(result), status=200, mimetype="application/json")

    @register_route("/<node_id>/all_property_chart_data")
    def getAllProperties(self, node_id):
        self._setupDBUS()
        all_property_histories = {}
        for prop in self._nodes.getAdditionalProperties(node_id):
            all_property_histories[prop] = self._nodes.getAdditionalPropertyHistory(node_id, prop)
        all_property_histories["temperature"] = self._nodes.getNodeTemperatureHistory(node_id)

        resources_gained = self._nodes.getResourcesGainedHistory(node_id)
        for key in resources_gained:
            all_property_histories["%s received" % key] = resources_gained[key]

        resources_produced = self._nodes.getResourcesProducedHistory(node_id)
        for key in resources_produced:
            all_property_histories["%s produced" % key] = resources_produced[str(key)]
        return Response(flask.json.dumps(all_property_histories), status=200, mimetype="application/json")

    @register_route("/<node_id>/connections/incoming")
    def getIncomingConnections(self, node_id):
        self._setupDBUS()

        data = self._nodes.getIncomingConnections(node_id)
        return Response(flask.json.dumps(data), status = 200, mimetype ="application/json")

    @register_route("/<node_id>/connections/outgoing")
    def getOutgoingConnections(self, node_id):
        self._setupDBUS()

        data = self._nodes.getOutgoingConnections(node_id)
        return Response(flask.json.dumps(data), status=200, mimetype="application/json")

    @register_route("/<node_id>/description")
    def getDescription(self, node_id):
        self._setupDBUS()

        data = self._nodes.getNodeDescription(node_id)
        return Response(flask.json.dumps(data), status=200, mimetype="application/json")


if __name__ == "__main__":
    Server().run(debug=True)
