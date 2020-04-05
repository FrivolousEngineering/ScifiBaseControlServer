from flask import Blueprint, Response, request
import flask
from flask import current_app as app
import json


node_blueprint = Blueprint('node', __name__)


@node_blueprint.route("/<node_id>/")
def nodeData(node_id: str):
    nodes = app.getDBusObject()
    data = getNodeData(node_id)
    data["surface_area"] = nodes.getSurfaceArea(node_id)  # type: ignore
    data["description"] = nodes.getDescription(node_id)  # type: ignore

    return Response(flask.json.dumps(data), status = 200, mimetype="application/json")


@node_blueprint.route("/<node_id>/enabled/", methods=["PUT", "GET"])
def nodeEnabled(node_id):
    nodes = app.getDBusObject()
    if request.method == "PUT":
        return setNodeEnabled(node_id)

    return Response(flask.json.dumps(nodes.isNodeEnabled(node_id)), status=200, mimetype="application/json")


def setNodeEnabled(node_id):
    nodes = app.getDBusObject()
    nodes.setNodeEnabled(node_id, not nodes.isNodeEnabled(node_id))
    return Response(flask.json.dumps({"message": ""}), status=200, mimetype="application/json")


@node_blueprint.route("/<node_id>/performance/", methods = ["PUT", "GET"])
def nodePerformance(node_id):
    nodes = app.getDBusObject()
    if request.method == "PUT":
        return setNodePerformance(node_id)

    return Response(flask.json.dumps(nodes.getPerformance(node_id)), status=200, mimetype="application/json")


def setNodePerformance(node_id):
    nodes = app.getDBusObject()
    if "performance" in request.form:
        new_performance = request.form["performance"]
    else:
        new_performance = json.loads(request.data)["performance"]
    nodes.setPerformance(node_id, float(new_performance))
    return Response(flask.json.dumps(nodes.getPerformance(node_id)), status=200, mimetype="application/json")


@node_blueprint.route("/<node_id>/temperature/history/")
def temperatureHistory(node_id):
    nodes = app.getDBusObject()
    result = nodes.getTemperatureHistory(node_id)  # type: ignore
    show_last = request.args.get("showLast")
    if show_last is not None and show_last:
        try:
            result = result[-int(show_last):]
        except ValueError:
            pass
    return Response(flask.json.dumps(result), status=200, mimetype="application/json")


@node_blueprint.route("/<node_id>/temperature/")
def temperature(node_id):
    nodes = app.getDBusObject()
    result = nodes.getTemperature(node_id)  # type: ignore
    return Response(flask.json.dumps(result), status=200, mimetype="application/json")


@node_blueprint.route("/<node_id>/<prop>/history/")
def additionalPropertyHistory(node_id, prop):
    nodes = app.getDBusObject()
    additional_property_history = nodes.getAdditionalPropertyHistory(node_id, prop)
    return Response(flask.json.dumps(additional_property_history), status=200, mimetype="application/json")


@node_blueprint.route("/<node_id>/additional_properties/")
def getAdditionalProperties(node_id):
    nodes = app.getDBusObject()
    additional_properties = nodes.getAdditionalProperties(node_id)
    result = {}
    for prop in additional_properties:
        result[prop] = {}
        result[prop]["max_value"] = nodes.getMaxAdditionalPropertyValue(node_id, prop)
        result[prop]["value"] = nodes.getAdditionalPropertyValue(node_id, prop)
    return Response(flask.json.dumps(result), status=200, mimetype="application/json")


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
