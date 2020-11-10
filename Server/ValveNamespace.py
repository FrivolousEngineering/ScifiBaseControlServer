from typing import Optional, Dict, Any

from flask import Blueprint, request, Response
from flask import current_app as app
from flask_restx import Resource, Api, apidoc, fields, Namespace, Model
import json


from Server.Blueprint import api

valve_namespace = Namespace("valve", description = "Valves are the remote devices that provide us with state.")

valve = api.model("valve", {
    "valve_id": fields.String
})


@valve_namespace.route("/")
@valve_namespace.doc(description = "Get all the known Valves.")
class Valves(Resource):
    @api.response(200, "Sucess", fields.List(fields.Nested(valve)))
    def get(self):
        return []


@valve_namespace.route("/<string:valve_id>/")
@valve_namespace.doc(params={'valve_id': 'Identifier of the valve'})
class Node(Resource):
    @api.response(200, "success", valve)
    @api.response(404, "Unknown Node")
    def get(self, node_id):
        return {}