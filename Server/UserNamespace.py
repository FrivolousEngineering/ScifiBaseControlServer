
from flask_restx import Resource, fields, Namespace
from Server.Blueprint import api
from Server.models import User

from flask import Response, request

User_namespace = Namespace("User", description = "TODO")


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
    "active_modifiers": fields.List(fields.Nested(modifier))
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
                    ]
                    }
