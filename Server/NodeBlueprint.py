from flask import Blueprint, Response, request
import flask
from flask import current_app as app
from flask_restplus import Resource, Api, apidoc, fields
import json


node_blueprint = Blueprint('node', __name__)
api = Api(node_blueprint, description="Node data. Yay")


@node_blueprint.route("/<node_id>/")
def nodeData(node_id: str):
    nodes = app.getDBusObject()
    data = getNodeData(node_id)
    data["surface_area"] = nodes.getSurfaceArea(node_id)  # type: ignore
    data["description"] = nodes.getDescription(node_id)  # type: ignore

    return Response(flask.json.dumps(data), status = 200, mimetype="application/json")

@api.route('/<string:node_id>/enabled/')
@api.doc(params={'node_id': 'Identifier of the node'})
class Enabled(Resource):
    @api.response(200, 'Success', fields.Boolean)
    def get(self, node_id):
        nodes = app.getDBusObject()

        return nodes.isNodeEnabled(node_id)

    def put(self, node_id):
        nodes = app.getDBusObject()
        nodes.setNodeEnabled(node_id, not nodes.isNodeEnabled(node_id))


performance_parser = api.parser()
performance_parser.add_argument('performance', type=float, help='New performance', location='form')

@api.route('/<string:node_id>/performance/')
@api.doc(params={'node_id': 'Identifier of the node'})
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


@api.route("/<node_id>/temperature/history/")
@api.doc(params={'node_id': 'Identifier of the node'})
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


@api.route("/<node_id>/temperature/")
@api.doc(params={'node_id': 'Identifier of the node'})
class Temperature(Resource):
    @api.response(200, 'Success', fields.Float)
    def get(self, node_id):
        nodes = app.getDBusObject()
        return nodes.getTemperature(node_id)


@api.route("/<node_id>/<prop>/history/")
@api.doc(params={'node_id': 'Identifier of the node'})
class AdditionalPropertyHistory(Resource):
    def get(self, node_id, prop):
        nodes = app.getDBusObject()
        return nodes.getAdditionalPropertyHistory(node_id, prop)


@api.route("/<node_id>/additional_properties/")
@api.doc(params={'node_id': 'Identifier of the node'})
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


@node_blueprint.route("/<node_id>/all_property_chart_data/")
def getAllProperties(node_id):
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
    return Response(flask.json.dumps(all_property_histories), status=200, mimetype="application/json")


@node_blueprint.route("/<node_id>/connections/incoming/")
def getIncomingConnections(node_id):
    nodes = app.getDBusObject()

    data = nodes.getIncomingConnections(node_id)
    return Response(flask.json.dumps(data), status = 200, mimetype ="application/json")


@node_blueprint.route("/<node_id>/connections/outgoing/")
def getOutgoingConnections(node_id):
    nodes = app.getDBusObject()

    data = nodes.getOutgoingConnections(node_id)
    return Response(flask.json.dumps(data), status=200, mimetype="application/json")


@node_blueprint.route("/<node_id>/modifiers/")
def getModifiers(node_id):
    nodes = app.getDBusObject()
    data = nodes.getActiveModifiers(node_id)
    return Response(flask.json.dumps(data), status=200, mimetype="application/json")


@node_blueprint.route("/<node_id>/static_properties/")
def getStaticProperties(node_id):
    nodes = app.getDBusObject()
    data = {}
    data["surface_area"] = nodes.getSurfaceArea(node_id)
    data["description"] = nodes.getDescription(node_id)
    return Response(flask.json.dumps(data), status=200, mimetype="application/json")


@node_blueprint.route("/<string:node_id>/<string:additional_property>/")
def getAdditionalPropertyValue(node_id, additional_property):
    nodes = app.getDBusObject()
    data = nodes.getAdditionalPropertyValue(node_id, additional_property)
    return Response(flask.json.dumps(data), status=200, mimetype="application/json")


@node_blueprint.route("/nodes/")
def getAllNodeData():
    nodes = app.getDBusObject()
    display_data = []
    for node_id in nodes.getAllNodeIds():  # type: ignore
        data = getNodeData(node_id)
        display_data.append(data)
    return Response(flask.json.dumps(display_data), status=200, mimetype="application/json")


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
