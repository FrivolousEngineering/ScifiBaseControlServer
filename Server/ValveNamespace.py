from typing import Optional, Dict, Any

from flask import Blueprint, request, Response
from flask import current_app as app
from flask_restx import Resource, Api, apidoc, fields, Namespace, Model
import json


from Server.Blueprint import api

valve_namespace = Namespace("valve", description = "Valves are the remote devices that provide us with state.")

@valve_namespace.route("/")
@valve_namespace.doc(description = "Get all the known Valves.")
class Valves(Resource):
    @api.response(200, "Sucess")
    def get(self):
        return ""
