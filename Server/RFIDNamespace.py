from Server.Blueprint import api
from flask_restx import Resource, Api, apidoc, fields, Namespace, Model
from flask import current_app as app
from Server.Blueprint import api
from Server.models import User, Ability, AccessCard
from Server.Database import db_session, getDBSession
from sqlalchemy import exc

from flask import Response, request

RFID_namespace = Namespace("RFID", description = "Users can authenticate themselves with RFID.")


UNKNOWN_CARD_RESPONSE = Response('{"message": "Unknown Card"}', status=404, mimetype='application/json')
CARD_UPDATE_FAILED = Response('{"message": "Card update failed"}', status=500, mimetype='application/json')
CARD_UPDATE_SUCCEEDED = Response('{"message": "Card updated"}', status=200, mimetype='application/json')
CARD_ADDED = Response('{"message": "Card Added"}', status=201, mimetype='application/json')

UNKNOWN_USER = Response('{"message": "The provided username was not found. Please create the user first!"}',
                        status = 404,
                        mimetype='application/json')

user_parser = api.parser()
user_parser.add_argument('user_name',
                         type = str,
                         help = 'Username that needs to be associated with the RFID badge',
                         location = 'form',
                         required = True)


access_card_model = api.model("access_card", {
    "id": fields.String(description = "Unique identifier of RFID card",
                             example = "some hex",
                             readonly = True),
    "user_name": fields.String(description = "Name of the user the card is attached to",
                             example = "admin")
})


@RFID_namespace.route("/")
@RFID_namespace.doc(description ="List all RFID cards in the database")
class AllCards(Resource):
    @api.response(200, "Success", fields.List(fields.Nested(access_card_model)))
    def get(self):
        return [{"id": card.id, "user_name": card.user.id} for card in AccessCard.query.all()]


@RFID_namespace.route("/<string:card_id>/")
@RFID_namespace.doc(description ="Influence a single RFID card")
class RFID(Resource):
    @api.response(200, "Success", access_card_model)
    @api.response(404, "Unknown Card")
    def get(self, card_id):
        access_card = AccessCard.query.filter_by(id = card_id).first()
        if not access_card:
            return UNKNOWN_CARD_RESPONSE
        else:
            return {"id": access_card.id, "user_name": access_card.user.id}

    @api.response(201, "Card was added to the database")
    @api.response(409, "Card already exists, unable to add it again")
    @api.response(404, "User not found")
    @api.response(400, "Bad request")
    @api.expect(user_parser)
    def post(self, card_id):
        access_card = AccessCard.query.filter_by(id=card_id).first()
        if access_card:
            return Response('{"message": "The provided card already exists. Unable to add it again"}',
                            status=409,
                            mimetype='application/json')

        user = User.query.filter_by(id = request.form["user_name"]).first()
        if not user:
            return UNKNOWN_USER

        user.access_cards.append(AccessCard(card_id))

        getDBSession().commit()
        return CARD_ADDED

    @api.response(404, "Unknown Card")
    @api.response(404, "Unknown User")
    @api.response(200, "Card Updated")
    @api.expect(user_parser)
    def put(self, card_id):
        access_card = AccessCard.query.filter_by(id=card_id).first()
        if not access_card:
            return UNKNOWN_CARD_RESPONSE
        user = User.query.filter_by(id=request.form["user_name"]).first()
        if not user:
            return UNKNOWN_USER

        access_card.user = user
        getDBSession().commit()
        return CARD_UPDATE_SUCCEEDED

# name, email are required for new users. Ability can be passed multiple times.
# Only adds abilities; does not remove them.
'''@RFID_namespace.route("/update/<string:card_id>/")
@RFID_namespace.doc(description = "Update a user's information")
class RFIDUpdate(Resource):
    @api.response(200, "User updated")
    @api.response(500, "User update failed")
    def post(self, card_id):
        user = User.query.filter_by(card_id = card_id).first()
        ability_list = request.args.getlist("ability")
        abilities = []
        for a in ability_list:
            ability = Ability.query.filter_by(name = a).first()
            abilities += [ability] if ability is not None else []
        if not user:
            name = request.args.get("name")
            email = request.args.get("email")
            user = User(card_id, name, email)
            user.abilities = abilities
            try:
                db_session.add(user)
                db_session.commit()
                return CARD_UPDATE_SUCCEEDED
            except exc.SQLAlchemyError:
                return CARD_UPDATE_FAILED
        else:
            user.abilities += abilities
            db_session.commit()
            return CARD_UPDATE_SUCCEEDED'''

