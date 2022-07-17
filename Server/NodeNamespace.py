from typing import Optional, Dict, Any, Union, List, cast

from flask import request, Response, make_response
from flask import current_app
from flask_restx import Resource, fields, Namespace

from Nodes.Constants import SPECIFIC_HEAT
from Nodes.NodesDBusService import NodesDBusService
from Server.Server import Server
from Server.Database import getDBSession
from Server.Blueprint import api

from Server.models import AccessCard, Modifier

import json

# Workaround so that mypy understands that the app is of type "Server" and not "Flask"
app = cast(Server, current_app)

node_namespace = Namespace("node", description = "Each node is a device in the system. These endpoints allow for individual control of each of them.")

resource_type_field = fields.String(description = "The type of resource for this connection", enum = list(SPECIFIC_HEAT.keys()))

connection = api.model("connection", {
    "target": fields.String(description = "Node that receives resources from this connection"),
    "origin": fields.String(description = "Node that provides resources for this connection"),
    "resource_type": resource_type_field
})

addit_property = api.model("addit_property",
{
    "key": fields.String,
    "value": fields.Float,
    "max_value": fields.Float
})

resource_amount = api.model("resource_amount", {
    "resource_type": resource_type_field,
    "value": fields.Float
})

modifier = api.model("modifier",
{
    "name": fields.String(description = "Human readable name of the modifier"),
    "duration": fields.Integer(description = "Number of ticks this modifier will remain active"),
    "abbreviation": fields.String(description = "Three letter abbreviation of this modifier")
})

static_properties = api.model("static_properties",
{
    "surface_area": fields.Float,
    "description": fields.String,
    "has_settable_performance": fields.Boolean,
    "supported_modifiers": fields.List(fields.String)
})

UNKNOWN_NODE_RESPONSE = Response("{\"message\": \"Could not find the requested node\"}", status=404, mimetype='application/json')

UNKNOWN_PROPERTY_RESPONSE = Response("{\"message\": \"Could not find the requested property\"}", status=404, mimetype='application/json')

CREDENTIALS_REQUIRED_RESPONSE = Response("{\"message\": \"Please provide an accessCardID\"}", status=401, mimetype='application/json')

UNKNOWN_ACCESS_CARD = Response("{\"message\": \"Access card ID is not recognised.\"}", status=401, mimetype='application/json')

INSUFFICIENT_RIGHTS = Response("{\"message\": \"User is not allowed to perform this action.\"}", status=403, mimetype='application/json')

node = api.model("node", {
    "node_id": fields.String(description = "Unique identifier of the node",
                             example = "generator",
                             readonly = True),
    "node_type": fields.String(description = "The type of the Node", example = "Generator", readonly = True),
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
    "resources_provided": fields.List(fields.Nested(resource_amount)),
    "optional_resources_required": fields.List(fields.Nested(resource_amount)),
    "additional_properties": fields.List(fields.Nested(addit_property)),
    "effectiveness_factor": fields.Float(description = "How well is this node performing? This factor can be influenced by it's health and the temperature of the node"),
    "label": fields.String(description = "Human readable name of the node", example = "Generator", readonly = True)
})


authorization_parser = api.parser()
authorization_parser.add_argument("accessCardID", type = str, required = True)

optional_authorization_parser = api.parser()
optional_authorization_parser.add_argument("accessCardID", type = str, required = False)

performance_parser = optional_authorization_parser.copy()
performance_parser.add_argument('performance', type=float, help='New performance', location='form')


modifier_parser = authorization_parser.copy()
modifier_parser.add_argument("modifier_name", location = "json", required = True)

show_last_parser = api.parser()
show_last_parser.add_argument("showLast", type = str, location='args')


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
        return bool(nodes.isNodeEnabled(node_id))

    @api.response(200, 'Success', fields.Boolean())
    @api.response(404, "Unknown Node")
    def put(self, node_id):
        nodes = app.getNodeDBusObject()
        if not checkIfNodeExists(nodes, node_id):
            return UNKNOWN_NODE_RESPONSE
        nodes.setNodeEnabled(node_id, not nodes.isNodeEnabled(node_id))
        return bool(nodes.isNodeEnabled(node_id))


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
    @api.response(400, "malformed request")
    @api.expect(performance_parser)
    def put(self, node_id):
        card_id = request.args.get("accessCardID")
        nodes = app.getNodeDBusObject()
        if not checkIfNodeExists(nodes, node_id):
            return UNKNOWN_NODE_RESPONSE

        performance_set = False
        if "performance" in request.form:
            new_performance = request.form["performance"]
            performance_set = True
        else:
            try:
                new_performance = json.loads(request.data)["performance"]
                performance_set = True
            except:
                pass
        if not performance_set:
            return Response("Performance must be set", status=400,
                            mimetype='application/json')

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
    @api.response(400, "malformed request")
    @api.expect(performance_parser)
    def put(self, node_id):
        nodes = app.getNodeDBusObject()
        if not checkIfNodeExists(nodes, node_id):
            return UNKNOWN_NODE_RESPONSE
        performance_set = False
        if "performance" in request.form:
            new_performance = request.form["performance"]
            performance_set = True
        else:
            try:
                new_performance = json.loads(request.data)["performance"]
                performance_set = True
            except:
                pass
        if not performance_set:
            return Response("Performance must be set", status=400,
                            mimetype='application/json')
        nodes.setTargetPerformance(node_id, float(new_performance))
        return nodes.getPerformance(node_id)


@node_namespace.route("/<string:node_id>/temperature/history/")
@node_namespace.doc(params={'node_id': 'Identifier of the node'}, description = "Get the history of the node in deg Kelvin")
class TemperatureHistory(Resource):
    @api.response(200, "success", fields.List(fields.Float))
    @api.response(404, "Unknown Node")
    @api.expect(show_last_parser)
    def get(self, node_id):
        nodes = app.getNodeDBusObject()
        if not checkIfNodeExists(nodes, node_id):
            return UNKNOWN_NODE_RESPONSE
        result = nodes.getTemperatureHistory(node_id)  # type: ignore
        args = show_last_parser.parse_args()
        show_last = args.get("showLast")
        if show_last is not None and show_last:
            try:
                result = result[-int(show_last):]
            except ValueError:
                pass
        return result


@node_namespace.route("/<string:node_id>/temperature/")
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


@node_namespace.route("/<string:node_id>/<string:prop>/history/")
@node_namespace.doc(params={'node_id': 'Identifier of the node'},
                    description = "Get the history of a certain attribute")
class AdditionalPropertyHistory(Resource):
    @api.response(404, "Unknown Node")
    @api.response(200, "success", fields.List(fields.Float))
    def get(self, node_id, prop):
        nodes = app.getNodeDBusObject()
        if not checkIfNodeExists(nodes, node_id):
            return UNKNOWN_NODE_RESPONSE
        try:
            return nodes.getAdditionalPropertyHistory(node_id, prop)
        except:
            return UNKNOWN_PROPERTY_RESPONSE


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


@node_namespace.route("/<string:node_id>/additional_properties/")
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


@node_namespace.route("/<string:node_id>/all_property_chart_data/")
@node_namespace.doc(description = "Get historical data for all prpoerties that can have a history")
class AllProperties(Resource):
    @api.response(200, "success")
    @api.response(404, "Unknown Node")
    @api.expect(show_last_parser)
    def get(self, node_id):
        args = show_last_parser.parse_args()
        show_last = args.get("showLast")
        nodes = app.getNodeDBusObject()
        if not checkIfNodeExists(nodes, node_id):
            return UNKNOWN_NODE_RESPONSE

        all_property_histories = {}
        all_property_histories["offset"] = nodes.getHistoryOffset(node_id)
        for prop in nodes.getAdditionalProperties(node_id):
            try:
                all_property_histories[prop] = nodes.getAdditionalPropertyHistory(node_id, prop)
            except ValueError:
                pass

        all_property_histories["temperature"] = nodes.getTemperatureHistory(node_id)
        try:
            resources_gained = nodes.getResourcesGainedHistory(node_id)
        except:
            resources_gained = {}

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


@node_namespace.route("/<string:node_id>/connections/incoming/")
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


@node_namespace.route("/<string:node_id>/connections/outgoing/")
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


@node_namespace.route("/<string:node_id>/modifiers/")
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
    @api.response(200, "Success")
    @api.response(403, "Insufficient Rights")
    @api.response(401, "Authentication required")
    @api.expect(modifier_parser)
    def post(self, node_id):
        nodes = app.getNodeDBusObject()
        if not checkIfNodeExists(nodes, node_id):
            return UNKNOWN_NODE_RESPONSE
        args = modifier_parser.parse_args()
        access_id = args.get("accessCardID")

        if not access_id:
            return CREDENTIALS_REQUIRED_RESPONSE

        access_card = AccessCard.query.filter_by(id = access_id).first()
        if not access_card:
            return UNKNOWN_ACCESS_CARD

        try:
            data = json.loads(request.data)
        except:
            return Response("Unable to format the provided data!", status = 400, mimetype='application/json')

        if "modifier_name" not in data:
            return Response('{"message": "modifier name must be set}"', status = 400, mimetype='application/json')

        # Engineering level defines how much modifiers you can place
        if access_card.user.engineering_level <= len(access_card.user.modifiers):
            # The exception to this if a user wants to 're-place' a modifier.
            is_replace = False
            for modifier in access_card.user.modifiers:
                if modifier.name == data["modifier_name"] and modifier.node_id == node_id:
                    is_replace = True
                    break
            if not is_replace:
                return INSUFFICIENT_RIGHTS

        successful = nodes.addModifierToNode(node_id, data["modifier_name"])
        if not successful:
            return Response("Unknown modifier", status = 400, mimetype='application/json')

        # Check if it was a modifier that was "replaced". Basically users can place a modifier again to reset the
        # duration. In that case it shouldn't add another item to the DB.
        modifier = Modifier.query.filter_by(name = data["modifier_name"], node_id = node_id).first()
        if modifier:
            # Another user (or the same) already had this active. Remove it!
            getDBSession().delete(modifier)

        # Add the modifier to the database!
        modifier = Modifier(data["modifier_name"], node_id)
        access_card.user.modifiers.append(modifier)
        getDBSession().commit()
        return nodes.getActiveModifiers(node_id)


@node_namespace.route("/<string:node_id>/static_properties/")
@node_namespace.doc(params={'node_id': 'Identifier of the node'}, description = "These are all the properties of the given node that can never change once a run has started.")
class StaticProperties(Resource):
    @api.response(404, "Unknown Node")
    @api.response(200, "Success", static_properties)
    def get(self, node_id):
        nodes = app.getNodeDBusObject()
        if not checkIfNodeExists(nodes, node_id):
            return UNKNOWN_NODE_RESPONSE
        data = {}
        data["surface_area"] = nodes.getSurfaceArea(node_id)
        data["description"] = nodes.getDescription(node_id)
        data["custom_description"] = nodes.getCustomDescription(node_id)
        data["has_settable_performance"] = bool(nodes.hasSettablePerformance(node_id))
        data["supported_modifiers"] = nodes.getSupportedModifiers(node_id)
        data["label"] = nodes.getLabel(node_id)
        data["node_type"] = nodes.getNodeType(node_id)
        return data


@node_namespace.route("/<string:node_id>/<string:additional_property>/")
@node_namespace.doc(params={'node_id': 'Identifier of the node',
                            "additional_property": "The name of the attribute to request"})
class AdditionalProperty(Resource):
    @api.response(404, "Unknown Node")
    @api.response(200, "success", fields.Float)
    def get(self, node_id, additional_property):
        nodes = app.getNodeDBusObject()
        if not checkIfNodeExists(nodes, node_id):
            return UNKNOWN_NODE_RESPONSE
        try:
            data = nodes.getAdditionalPropertyValue(node_id, additional_property)
        except:
            return UNKNOWN_PROPERTY_RESPONSE
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

    resources_provided = []
    for key, value in nodes.getResourcesProvided(node_id).items():
        resources_provided.append({"resource_type": key, "value": value})

    data = {"node_id": node_id,
            "node_type": nodes.getNodeType(node_id),
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
            "resources_provided": resources_provided,
            "additional_properties": getAdditionalPropertiesForNode(node_id),
            "effectiveness_factor": nodes.getEffectivenessFactor(node_id),
            "label": nodes.getLabel(node_id)
            }
    return data
