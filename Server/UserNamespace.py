from typing import cast

from flask_restx import Resource, fields, Namespace
from Server.Blueprint import api
from Server.Database import getDBSession
from Server.models import User

from flask import Response, request, current_app
from Server.Server import Server

User_namespace = Namespace("user", description = "Management for all users in this system")


# Workaround so that mypy understands that the app is of type "Server" and not "Flask"
app = cast(Server, current_app)

UNKNOWN_USER_RESPONSE = Response('{"message": "Unknown User"}', status = 404, mimetype = 'application/json')
USER_ADDED = Response('{"message": "User Added"}', status = 201, mimetype = 'application/json')
USER_UPDATE_SUCCEEDED = Response('{"message": "User updated"}', status = 200, mimetype = 'application/json')

modifier = api.model("active_modifier", {
    "name": fields.String(description = "Name of the modifier that is placed"),
    "node_id": fields.String(description = "ID of the node that it's placed on")
})

user_model = api.model("node", {
    "id": fields.String(description = "Unique identifier of the user",
                             example = "admin",
                             readonly = True),
    "access_cards": fields.List(fields.String(description = "unique key of the access card")),
    "active_modifiers": fields.List(fields.Nested(modifier)),
    "engineering_level": fields.Integer(description = "The engineering level of this user. This is 0 by default"),
    "faction": fields.String(description = "The faction that the user belongs to", enum = ["Deimian", "Rhean", "Keplian"])
    })


def createUserModel(user):
    return {"id": user.id,
            "access_cards": [access_card.id for access_card in user.access_cards],
            "active_modifiers": [
                {
                    "name": modifier.name,
                    "node_id": modifier.node_id
                } for modifier in user.modifiers
            ],
            "engineering_level": user.engineering_level,
            "faction": user.faction
            }


@User_namespace.route("/")
@User_namespace.doc(description = "All users")
class AllUsers(Resource):
    @api.response(200, "Success", fields.List(fields.Nested(user_model)))
    def get(self):
        result = []
        for user in User.query.all():
            result.append(createUserModel(user))
        return result


user_parser = api.parser()
user_parser.add_argument('engineering_level',
                         type = int,
                         help = 'The engineering level of the user. This is 0 by default',
                         location = 'form',
                         default = 0)
user_parser.add_argument("faction",
                         type = str,
                         help = "What faction does the user belong to?",
                         location = "form",
                         choices = ("Deimian", "Rhean", "Keplian"),
                         required = True)

user_parser_put = api.parser()
user_parser_put.add_argument('engineering_level',
                                type = int,
                                help = 'The engineering level of the user.',
                                location = 'form',
                                required = True)


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
            return createUserModel(user)

    @api.response(409, "User already exists")
    @api.response(201, "User was added to the database")
    @api.response(400, "Invalid data")
    @api.expect(user_parser)
    def post(self, user_id):
        user = User.query.filter_by(id=user_id).first()
        if user:
            return Response('{"message": "The provided user already exists. Unable to add it again"}',
                            status=409,
                            mimetype='application/json')
        args = user_parser.parse_args()
        engineering_level = args.get("engineering_level", 0)
        if engineering_level > 100:
            engineering_level = 100
        if engineering_level < 0:
            engineering_level = 0
        new_user = User(user_id, args["faction"], engineering_level)
        db_session = getDBSession()
        db_session.add(new_user)
        db_session.commit()

        return USER_ADDED

    @api.response(404, "Unknown User")
    @api.response(200, "User Updated")
    @api.response(400, "Invalid data")
    @api.expect(user_parser)
    def put(self, user_id):
        user = User.query.filter_by(id=user_id).first()
        if not user:
            return UNKNOWN_USER_RESPONSE

        args = user_parser.parse_args()
        engineering_level = args.get("engineering_level", 0)
        if engineering_level > 100:
            engineering_level = 100
        if engineering_level < 0:
            engineering_level = 0
        user.engineering_level = engineering_level
        getDBSession().commit()
        return USER_UPDATE_SUCCEEDED


