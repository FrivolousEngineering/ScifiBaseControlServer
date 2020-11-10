from flask import request
from flask_restx import Resource, fields, Namespace
import json
from Server.Blueprint import api
from Server.ControllerManager import ControllerManager


control_namespace = Namespace("controller", description ="Controllers are the remote devices that provide us with state.")

controller = api.model("controller", {
    "controller_id": fields.String
})


@control_namespace.route("/")
@control_namespace.doc(description ="Get all the known controllers.")
class Controllers(Resource):
    @api.response(200, "Sucess", fields.List(fields.Nested(controller)))
    def get(self):
        return []


@control_namespace.route("/<string:controller_id>/")
@control_namespace.doc(params={'controller_id': 'Identifier of the controller'})
class Controller(Resource):
    @api.response(200, "success", controller)
    @api.response(404, "Unknown Node")
    def get(self, controller_id):
        manager = ControllerManager.getInstance()
        controller = manager.getController(controller_id)
        if controller is None:
            return {}
        return {"id": controller_id,
                "time_since_last_update": controller.time_since_last_update}

    @api.response(200, "success")
    def put(self, controller_id):
        manager = ControllerManager.getInstance()
        manager.updateController(controller_id, json.loads(request.data))
