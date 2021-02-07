from Server.Blueprint import api
from flask_restx import Resource, Api, apidoc, fields, Namespace, Model
from flask import current_app as app
from Server.Blueprint import api

from flask import Response

RFID_namespace = Namespace("RFID", description = "Users can authenticate themselves with RFID.")


UNKNOWN_CARD_RESPONSE = Response("Unknown Card", status=404)


@RFID_namespace.route("/<string:card_id>/")
@RFID_namespace.doc(description ="Get all modifier types")
class RFID(Resource):
    @api.response(200, "success")
    @api.response(404, "Unknown Card")
    def get(self, card_id):
        # TODO: Actually check a database for the known cards.
        if card_id != "8666529cc":
            return UNKNOWN_CARD_RESPONSE
        else:
            return "Welcome back!"



