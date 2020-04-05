from flask import Blueprint, Response, request
import flask
from flask import current_app as app
from flask_restplus import Resource, Api, apidoc, fields, Namespace, Model
import json


node_blueprint = Blueprint('node', __name__)
api = Api(node_blueprint, description="Node data. Yay")
node_namespace = Namespace("node", description = "omgzomgbbq")

api.add_namespace(node_namespace)

connection = api.model("connection", {
    "target": fields.String,
    "origin": fields.String,
    "resource_type": fields.String
})

node = api.model("node", {
    "node_id": fields.String,
    "temperature": fields.Float,
    "amount": fields.Float,
    "performance": fields.Float,
    "min_performance": fields.Float,
    "max_performance": fields.Float,
    "max_safe_temperature": fields.Float,
    "heat_convection": fields.Float,
    "heat_emissivity": fields.Float
})


@node_namespace.route("/<node_id>/")
@node_namespace.doc(params={'node_id': 'Identifier of the node'})
class Node(Resource):
    @api.response(200, "success", node)
    def get(self, node_id):
        nodes = app.getDBusObject()
        data = getNodeData(node_id)
        data["surface_area"] = nodes.getSurfaceArea(node_id)  # type: ignore
        data["description"] = nodes.getDescription(node_id)  # type: ignore
        return data


@node_namespace.route('/<string:node_id>/enabled/')
@node_namespace.doc(params={'node_id': 'Identifier of the node'})
class Enabled(Resource):
    @api.response(200, 'Success', fields.Boolean())
    def get(self, node_id):
        nodes = app.getDBusObject()

        return nodes.isNodeEnabled(node_id)

    def put(self, node_id):
        nodes = app.getDBusObject()
        nodes.setNodeEnabled(node_id, not nodes.isNodeEnabled(node_id))


performance_parser = api.parser()
performance_parser.add_argument('performance', type=float, help='New performance', location='form')


@node_namespace.route('/<string:node_id>/performance/')
@node_namespace.doc(params={'node_id': 'Identifier of the node'})
class Performance(Resource):
    @api.response(200, 'Success', fields.Float(default = 1))
    def get(self, node_id):
        nodes = app.getDBusObject()
        return nodes.getPerformance(node_id)

    @api.response(200, 'Success', fields.Float)
    @api.expect(performance_parser)
    def put(self, node_id):
        nodes = app.getDBusObject()
        if "performance" in request.form:
            new_performance = request.form["performance"]
        else:
            new_performance = json.loads(request.data)["performance"]
        nodes.setPerformance(node_id, float(new_performance))
        return nodes.getPerformance(node_id)


@node_blueprint.route('/doc/')
def swagger_ui():
    return apidoc.ui_for(api)


@node_namespace.route("/<node_id>/temperature/history/")
@node_namespace.doc(params={'node_id': 'Identifier of the node'})
class TemperatureHistory(Resource):
    @api.response(200, "success", fields.List(fields.Float))
    def get(self, node_id):
        nodes = app.getDBusObject()
        result = nodes.getTemperatureHistory(node_id)  # type: ignore
        show_last = request.args.get("showLast")
        if show_last is not None and show_last:
            try:
                result = result[-int(show_last):]
            except ValueError:
                pass
        return result


@node_namespace.route("/<node_id>/temperature/")
@node_namespace.doc(params={'node_id': 'Identifier of the node'},
                    description = "Get the temperature of the node in deg Kelvin")
class Temperature(Resource):
    @api.response(200, 'Success', fields.Float)
    def get(self, node_id):
        nodes = app.getDBusObject()
        return nodes.getTemperature(node_id)


@node_namespace.route("/<node_id>/<prop>/history/")
@node_namespace.doc(params={'node_id': 'Identifier of the node'},
                    description = "Get the history of a certain attribute")
class AdditionalPropertyHistory(Resource):
    def get(self, node_id, prop):
        nodes = app.getDBusObject()
        return nodes.getAdditionalPropertyHistory(node_id, prop)


@node_namespace.route("/<node_id>/additional_properties/")
@node_namespace.doc(params={'node_id': 'Identifier of the node'},
                    description = "Get the value of all extra attributes")
class AdditionalProperties(Resource):
    @api.response(200, "success", fields.List(fields.Float))
    def get(self, node_id):
        nodes = app.getDBusObject()
        additional_properties = nodes.getAdditionalProperties(node_id)
        result = {}
        for prop in additional_properties:
            result[prop] = {}
            result[prop]["max_value"] = nodes.getMaxAdditionalPropertyValue(node_id, prop)
            result[prop]["value"] = nodes.getAdditionalPropertyValue(node_id, prop)
        return result


@node_namespace.route("/<node_id>/all_property_chart_data/")
class AllProperties(Resource):
    def get(self, node_id):
        show_last = request.args.get("showLast")

        nodes = app.getDBusObject()
        all_property_histories = {}
        for prop in nodes.getAdditionalProperties(node_id):
            all_property_histories[prop] = nodes.getAdditionalPropertyHistory(node_id, prop)

        all_property_histories["temperature"] = nodes.getTemperatureHistory(node_id)

        resources_gained = nodes.getResourcesGainedHistory(node_id)
        for key in resources_gained:
            all_property_histories["%s received" % key] = resources_gained[key]

        resources_produced = nodes.getResourcesProducedHistory(node_id)
        for key in resources_produced:
            all_property_histories["%s produced" % key] = resources_produced[str(key)]

        for key in all_property_histories:
            if show_last is not None and show_last:
                try:
                    all_property_histories[key] = all_property_histories[key][-int(show_last):]
                except ValueError:
                    pass
        return all_property_histories


@node_namespace.route("/<node_id>/connections/incoming/")
@node_namespace.doc(params={'node_id': 'Identifier of the node'},
                    description = "Get a list of all connections that connect to this node")
class IncomingConnections(Resource):
    @api.response(200, 'Success', [connection])
    def get(self, node_id):
        nodes = app.getDBusObject()
        return nodes.getIncomingConnections(node_id)


@node_namespace.route("/<node_id>/connections/outgoing/")
@node_namespace.doc(params={'node_id': 'Identifier of the node'},
                    description = "Get a list of all connections that connect from this node")
class OutgoingConnections(Resource):
    @api.response(200, 'Success', [connection])
    def get(self, node_id):
        nodes = app.getDBusObject()
        return nodes.getOutgoingConnections(node_id)


@node_namespace.route("/<node_id>/modifiers/")
@node_namespace.doc(params={'node_id': 'Identifier of the node'})
class Modifiers(Resource):
    def get(self, node_id):
        nodes = app.getDBusObject()
        return nodes.getActiveModifiers(node_id)


@node_namespace.route("/<node_id>/static_properties/")
@node_namespace.doc(params={'node_id': 'Identifier of the node'})
class StaticProperties(Resource):
    def get(self, node_id):
        nodes = app.getDBusObject()
        data = {}
        data["surface_area"] = nodes.getSurfaceArea(node_id)
        data["description"] = nodes.getDescription(node_id)
        return data


@node_namespace.route("/<string:node_id>/<string:additional_property>/")
@node_namespace.doc(params={'node_id': 'Identifier of the node',
                            "additional_property": "name of the attribute"})
class AdditionalProperty(Resource):
    def get(self, node_id, additional_property):
        nodes = app.getDBusObject()
        data = nodes.getAdditionalPropertyValue(node_id, additional_property)
        return data


@node_namespace.route("/")
@node_namespace.doc(description = "Get all the known nodes.")
class Nodes(Resource):
    @api.response(200, "Sucess", fields.List(fields.Nested(node)))
    def get(self):
        nodes = app.getDBusObject()
        display_data = []
        for node_id in nodes.getAllNodeIds():  # type: ignore
            data = getNodeData(node_id)
            display_data.append(data)
        return display_data


def getNodeData(node_id: str):
    nodes = app.getDBusObject()
    data = {"node_id": node_id,
            "temperature": nodes.getTemperature(node_id),
            "amount": round(nodes.getAmountStored(node_id), 2),
            "enabled": nodes.isNodeEnabled(node_id),
            "active": nodes.isNodeActive(node_id),
            "performance": nodes.getPerformance(node_id),
            "min_performance": nodes.getMinPerformance(node_id),
            "max_performance": nodes.getMaxPerformance(node_id),
            "max_safe_temperature": nodes.getMaxSafeTemperature(node_id),
            "heat_convection": nodes.getHeatConvectionCoefficient(node_id),
            "heat_emissivity": nodes.getHeatEmissivity(node_id)
            }
    return data
