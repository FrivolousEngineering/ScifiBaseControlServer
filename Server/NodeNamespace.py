from typing import Optional, Dict, Any, Union, List, cast

from flask import request, Response
from flask import current_app
from flask_restx import Resource,fields, Namespace

from Nodes.NodesDBusService import NodesDBusService
from Server.Server import Server
from Server.Blueprint import api

import json

# Workaround so that mypy understands that the app is of type "Server" and not "Flask"
app = cast(Server, current_app)

node_namespace = Namespace("node", description = "Each node is a device in the system. These endpoints allow for individual control of each of them.")

connection = api.model("connection", {
    "target": fields.String,
    "origin": fields.String,
    "resource_type": fields.String
})

addit_property = api.model("addit_property",
{
    "key": fields.String,
    "value": fields.Float,
    "max_value": fields.Float
})

resource_amount = api.model("resource_amount", {
    "resource_type": fields.String,
    "value": fields.Float
})

modifier = api.model("modifier",
{
    "name": fields.String(description = "Human readable name of the modifier"),
    "duration": fields.Integer(description = "Number of ticks this modifier will remain active"),
    "abbreviation": fields.String(description = "Three letter abbreviation of this modifier")
})

UNKNOWN_NODE_RESPONSE = Response("Could not find the requested node", status=404)

node = api.model("node", {
    "node_id": fields.String(description = "Unique identifier of the node",
                             example = "generator",
                             readonly = True),
    "temperature": fields.Float(description = "Temperature of this node in degrees Kevlin",
                                example = 273.3),
    "performance": fields.Float(description = "At what capacity is this node running? The number is a factor and will always be between min_performance and max_performance",
                                example = 1),
    "target_performance": fields.Float(description = "What performance / capacity level is this node trying to reach? Note that not all nodes have an instant change, so it's target can be different from it's actual performance ",
                                       example = 1),
    "min_performance": fields.Float(description = "What is the minimum value of performance that this node can have?",
                                    example = 0.5),
    "max_performance": fields.Float(description = "What is the max value of performance that this node can have?",
                                    example = 1.5),
    "max_safe_temperature": fields.Float(description = "From what temperature up will this node start getting damage?",
                                         example = 500),
    "heat_convection": fields.Float,
    "heat_emissivity": fields.Float,
    "health": fields.Float(description = "How much health does this node have? This usually runs from 0 to 100.",
                           example = 50,
                           readonly = True),
    "is_temperature_dependant": fields.Boolean(description = "Is this node influenced by it's temperature?"),
    "optimal_temperature": fields.Float(description = "What is the most optimal temperature for this node?"),
    "resources_required": fields.List(fields.Nested(resource_amount)),
    "resources_received": fields.List(fields.Nested(resource_amount)),
    "resources_produced": fields.List(fields.Nested(resource_amount)),
    "optional_resources_required": fields.List(fields.Nested(resource_amount)),
    "additional_properties": fields.List(fields.Nested(addit_property)),
    "effectiveness_factor": fields.Float(description = "How well is this node performing? This factor can be influenced by it's health and the temperature of the node")
})


def checkIfNodeExists(nodes: "NodesDBusService", node_id: str) -> bool:
    try:
        return nodes.doesNodeExist(node_id)
    except:
        return False


@node_namespace.route("/<string:node_id>/")
@node_namespace.doc(params={'node_id': 'Identifier of the node'})
class Node(Resource):
    @api.response(200, "success", node)
    @api.response(404, "Unknown Node")
    def get(self, node_id):
        nodes = app.getNodeDBusObject()
        data = getNodeData(node_id)
        if data is None:
            return UNKNOWN_NODE_RESPONSE
        data["surface_area"] = nodes.getSurfaceArea(node_id)  # type: ignore
        data["description"] = nodes.getDescription(node_id)  # type: ignore
        return data


@node_namespace.route('/<string:node_id>/enabled/')
@node_namespace.doc(params={'node_id': 'Identifier of the node'})
class Enabled(Resource):
    @api.response(200, 'Success', fields.Boolean())
    @api.response(404, "Unknown Node")
    def get(self, node_id):
        nodes = app.getNodeDBusObject()
        if not checkIfNodeExists(nodes, node_id):
            return UNKNOWN_NODE_RESPONSE
        return nodes.isNodeEnabled(node_id)

    @api.response(404, "Unknown Node")
    def put(self, node_id):
        nodes = app.getNodeDBusObject()
        if not checkIfNodeExists(nodes, node_id):
            return UNKNOWN_NODE_RESPONSE
        nodes.setNodeEnabled(node_id, not nodes.isNodeEnabled(node_id))


performance_parser = api.parser()
performance_parser.add_argument('performance', type=float, help='New performance', location='form')


@node_namespace.route('/<string:node_id>/performance/')
@node_namespace.doc(params={'node_id': 'Identifier of the node'})
class Performance(Resource):
    @api.response(200, 'Success', fields.Float(default = 1))
    @api.response(404, "Unknown Node")
    def get(self, node_id):
        nodes = app.getNodeDBusObject()
        if not checkIfNodeExists(nodes, node_id):
            return UNKNOWN_NODE_RESPONSE
        return float(nodes.getPerformance(node_id))

    @api.response(200, 'Success', fields.Float)
    @api.response(404, "Unknown Node")
    @api.expect(performance_parser)
    def put(self, node_id):
        nodes = app.getNodeDBusObject()
        if not checkIfNodeExists(nodes, node_id):
            return UNKNOWN_NODE_RESPONSE
        if "performance" in request.form:
            new_performance = request.form["performance"]
        else:
            new_performance = json.loads(request.data)["performance"]
        nodes.setTargetPerformance(node_id, float(new_performance))
        return nodes.getPerformance(node_id)


@node_namespace.route('/<string:node_id>/target_performance/')
@node_namespace.doc(params={'node_id': 'Identifier of the node'})
class TargetPerformance(Resource):
    @api.response(200, 'Success', fields.Float(default = 1))
    @api.response(404, "Unknown Node")
    def get(self, node_id):
        nodes = app.getNodeDBusObject()
        if not checkIfNodeExists(nodes, node_id):
            return UNKNOWN_NODE_RESPONSE
        return nodes.getTargetPerformance(node_id)

    @api.response(200, 'Success', fields.Float)
    @api.response(404, "Unknown Node")
    @api.expect(performance_parser)
    def put(self, node_id):
        nodes = app.getNodeDBusObject()
        if not checkIfNodeExists(nodes, node_id):
            return UNKNOWN_NODE_RESPONSE
        if "performance" in request.form:
            new_performance = request.form["performance"]
        else:
            new_performance = json.loads(request.data)["performance"]
        nodes.setTargetPerformance(node_id, float(new_performance))
        return nodes.getPerformance(node_id)


@node_namespace.route("/<node_id>/temperature/history/")
@node_namespace.doc(params={'node_id': 'Identifier of the node'})
class TemperatureHistory(Resource):
    @api.response(200, "success", fields.List(fields.Float))
    @api.response(404, "Unknown Node")
    def get(self, node_id):
        nodes = app.getNodeDBusObject()
        if not checkIfNodeExists(nodes, node_id):
            return UNKNOWN_NODE_RESPONSE
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
    @api.response(404, "Unknown Node")
    def get(self, node_id):
        nodes = app.getNodeDBusObject()
        if not checkIfNodeExists(nodes, node_id):
            return UNKNOWN_NODE_RESPONSE
        return nodes.getTemperature(node_id)


@node_namespace.route("/<node_id>/<prop>/history/")
@node_namespace.doc(params={'node_id': 'Identifier of the node'},
                    description = "Get the history of a certain attribute")
class AdditionalPropertyHistory(Resource):
    @api.response(404, "Unknown Node")
    def get(self, node_id, prop):
        nodes = app.getNodeDBusObject()
        if not checkIfNodeExists(nodes, node_id):
            return UNKNOWN_NODE_RESPONSE
        return nodes.getAdditionalPropertyHistory(node_id, prop)


def getAdditionalPropertiesForNode(node_id: str) -> Optional[List[Dict[str, Union[str, float]]]]:
    nodes = app.getNodeDBusObject()
    if not checkIfNodeExists(nodes, node_id):
        return None
    additional_properties = nodes.getAdditionalProperties(node_id)
    result = []
    for prop in additional_properties:
        item = {}
        item["key"] = prop
        item["value"] = nodes.getAdditionalPropertyValue(node_id, prop)
        item["max_value"] = nodes.getMaxAdditionalPropertyValue(node_id, prop)
        result.append(item)
    return result


@node_namespace.route("/<node_id>/additional_properties/")
@node_namespace.doc(params={'node_id': 'Identifier of the node'},
                    description = "Get the value of all extra attributes")
class AdditionalProperties(Resource):
    @api.response(200, "success", [addit_property])
    @api.response(404, "Unknown Node")
    def get(self, node_id):
        result = getAdditionalPropertiesForNode(node_id)
        if result is None:
            return UNKNOWN_NODE_RESPONSE
        return result


@node_namespace.route("/<node_id>/all_property_chart_data/")
class AllProperties(Resource):
    @api.response(404, "Unknown Node")
    def get(self, node_id):
        show_last = request.args.get("showLast")
        nodes = app.getNodeDBusObject()
        if not checkIfNodeExists(nodes, node_id):
            return UNKNOWN_NODE_RESPONSE

        all_property_histories = {}

        all_property_histories["offset"] = nodes.getHistoryOffset(node_id)
        for prop in nodes.getAdditionalProperties(node_id):
            all_property_histories[prop] = nodes.getAdditionalPropertyHistory(node_id, prop)

        all_property_histories["temperature"] = nodes.getTemperatureHistory(node_id)

        resources_gained = nodes.getResourcesGainedHistory(node_id)
        for key in resources_gained:
            all_property_histories["%s received" % key] = resources_gained[key]

        resources_produced = nodes.getResourcesProducedHistory(node_id)
        for key in resources_produced:
            all_property_histories["%s produced" % key] = resources_produced[str(key)]

        resources_provided = nodes.getResourcesProvidedHistory(node_id)
        for key in resources_provided:
            all_property_histories["%s provided" % key] = resources_provided[str(key)]

        for key in all_property_histories:
            if show_last is not None and show_last and key != "offset":
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
    @api.response(404, "Unknown Node")
    def get(self, node_id):
        nodes = app.getNodeDBusObject()
        if not checkIfNodeExists(nodes, node_id):
            return UNKNOWN_NODE_RESPONSE
        return nodes.getIncomingConnections(node_id)


@node_namespace.route("/<node_id>/connections/outgoing/")
@node_namespace.doc(params={'node_id': 'Identifier of the node'},
                    description = "Get a list of all connections that connect from this node")
class OutgoingConnections(Resource):
    @api.response(200, 'Success', [connection])
    @api.response(404, "Unknown Node")
    def get(self, node_id):
        nodes = app.getNodeDBusObject()
        if not checkIfNodeExists(nodes, node_id):
            return UNKNOWN_NODE_RESPONSE

        return nodes.getOutgoingConnections(node_id)


@node_namespace.route("/<node_id>/modifiers/")
@node_namespace.doc(params={'node_id': 'Identifier of the node'})
class Modifiers(Resource):
    @api.response(404, "Unknown Node")
    @api.response(200, "Success'", [modifier])
    def get(self, node_id):
        nodes = app.getNodeDBusObject()
        if not checkIfNodeExists(nodes, node_id):
            return UNKNOWN_NODE_RESPONSE
        return nodes.getActiveModifiers(node_id)

    @api.response(404, "Unknown Node")
    @api.response(400, "Bad Request")
    @api.response(200, "Success'")
    def post(self, node_id):
        nodes = app.getNodeDBusObject()
        if not checkIfNodeExists(nodes, node_id):
            return UNKNOWN_NODE_RESPONSE

        try:
            data = json.loads(request.data)
        except:
            return Response("Unable to format the provided data!", status = 400)
        successful = nodes.addModifierToNode(node_id, data["modifier_name"])
        if not successful:
            return Response("Unknown modifier", status = 400)
        return nodes.getActiveModifiers(node_id)


@node_namespace.route("/<node_id>/static_properties/")
@node_namespace.doc(params={'node_id': 'Identifier of the node'})
class StaticProperties(Resource):
    @api.response(404, "Unknown Node")
    def get(self, node_id):
        nodes = app.getNodeDBusObject()
        if not checkIfNodeExists(nodes, node_id):
            return UNKNOWN_NODE_RESPONSE
        data = {}
        data["surface_area"] = nodes.getSurfaceArea(node_id)
        data["description"] = nodes.getDescription(node_id)
        data["has_settable_performance"] = nodes.hasSettablePerformance(node_id)
        data["supported_modifiers"] = nodes.getSupportedModifiers(node_id)
        return data


@node_namespace.route("/<string:node_id>/<string:additional_property>/")
@node_namespace.doc(params={'node_id': 'Identifier of the node',
                            "additional_property": "The name of the attribute to request"})
class AdditionalProperty(Resource):
    @api.response(404, "Unknown Node")
    def get(self, node_id, additional_property):
        nodes = app.getNodeDBusObject()
        if not checkIfNodeExists(nodes, node_id):
            return UNKNOWN_NODE_RESPONSE
        data = nodes.getAdditionalPropertyValue(node_id, additional_property)
        return data


@node_namespace.route("/")
@node_namespace.doc(description = "Get all the known nodes.")
class Nodes(Resource):
    @api.response(200, "Sucess", fields.List(fields.Nested(node)))
    def get(self):
        nodes = app.getNodeDBusObject()
        display_data = []
        for node_id in nodes.getAllNodeIds():  # type: ignore
            data = getNodeData(node_id)
            display_data.append(data)
        return display_data


def getNodeData(node_id: str) -> Optional[Dict[str, Any]]:
    nodes = app.getNodeDBusObject()
    if node_id not in nodes.getAllNodeIds():
        return None

    required_resources = []

    for key, value in nodes.getResourcesRequired(node_id).items():
        required_resources.append({"resource_type": key, "value": value})

    received_resources = []
    for key, value in nodes.getResourcesReceived(node_id).items():
        received_resources.append({"resource_type": key, "value": value})

    optional_required_resources = []
    for key, value in nodes.getOptionalResourcesRequired(node_id).items():
        optional_required_resources.append({"resource_type": key, "value": value})
        
    resources_produced = []
    for key, value in nodes.getResourcesProduced(node_id).items():
        resources_produced.append({"resource_type": key, "value": value})

    data = {"node_id": node_id,
            "temperature": nodes.getTemperature(node_id),
            "enabled": nodes.isNodeEnabled(node_id),
            "active": nodes.isNodeActive(node_id),
            "performance": nodes.getPerformance(node_id),
            "target_performance": nodes.getTargetPerformance(node_id),
            "min_performance": nodes.getMinPerformance(node_id),
            "max_performance": nodes.getMaxPerformance(node_id),
            "max_safe_temperature": nodes.getMaxSafeTemperature(node_id),
            "heat_convection": nodes.getHeatConvectionCoefficient(node_id),
            "heat_emissivity": nodes.getHeatEmissivity(node_id),
            "health": nodes.getAdditionalPropertyValue(node_id, "health"),
            "is_temperature_dependant": bool(nodes.getIsTemperatureDependant(node_id)),
            "optimal_temperature": nodes.getOptimalTemperature(node_id),
            "resources_required": required_resources,
            "optional_resources_required": optional_required_resources,
            "resources_received": received_resources,
            "resources_produced": resources_produced,
            "additional_properties": getAdditionalPropertiesForNode(node_id),
            "effectiveness_factor": nodes.getEffectivenessFactor(node_id)
            }
    return data
