from typing import cast

from flask_restx import Resource, fields, Namespace
from Server.Blueprint import api
from Server.models import User

from flask import Response, request, current_app
from Server.Server import Server

User_namespace = Namespace("User", description = "TODO")


# Workaround so that mypy understands that the app is of type "Server" and not "Flask"
app = cast(Server, current_app)

UNKNOWN_USER_RESPONSE = Response('{"message": "Unknown User"}', status=404, mimetype='application/json')

modifier = api.model("modifier", {
    "name": fields.String(description = "Name of the modifier that is placed"),
    "node_id": fields.String(description = "ID of the node that it's placed on")
})

user_model = api.model("node", {
    "id": fields.String(description = "Unique identifier of the user",
                             example = "admin",
                             readonly = True),
    "access_cards": fields.List(fields.String(description = "unique key of the access card")),
    "active_modifiers": fields.List(fields.Nested(modifier)),
    "engineering_level": fields.Integer(description = "The engineering level of this user. This is 0 by default")
    })


@User_namespace.route("/<string:user_id>/")
@User_namespace.doc(description = "Get User info")
class UserResource(Resource):
    @api.response(200, "Success", user_model)
    @api.response(404, "Unknown User")
    def get(self, user_id):
        user = User.query.filter_by(id = user_id).first()
        if not user:
            return UNKNOWN_USER_RESPONSE
        else:
            return {"id": user.id,
                    "access_cards": [access_card.id for access_card in user.access_cards],
                    "active_modifiers": [
                        {
                            "name": modifier.name,
                            "node_id": modifier.node_id
                        } for modifier in user.modifiers
                    ],
                    "engineering_level": user.engineering_level
                    }
