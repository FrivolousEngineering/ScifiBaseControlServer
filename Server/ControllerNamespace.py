from flask import request
from flask_restx import Resource, fields, Namespace

from Server.Blueprint import api

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
        return {}

    @api.response(200, "success")
    def put(self, controller_id):
        print(request.data)
        print("YAY GOT AN UPDATE")
