from Server.Blueprint import api
from flask_restx import Resource, Api, apidoc, fields, Namespace, Model
from flask import current_app as app
from Server.Blueprint import api
from Server.models import User, Ability, AccessCard
from Server.Database import db_session
from sqlalchemy import exc

from flask import Response, request

RFID_namespace = Namespace("RFID", description = "Users can authenticate themselves with RFID.")


UNKNOWN_CARD_RESPONSE = Response('{"message": "Unknown Card"}', status=404, mimetype='application/json')
CARD_UPDATE_FAILED = Response('{"message": "User update failed"}', status=500, mimetype='application/json')
CARD_UPDATE_SUCCEEDED = Response('{"message": "User updated"}', status=200, mimetype='application/json')


@RFID_namespace.route("/<string:card_id>/")
@RFID_namespace.doc(description ="Get RFID card data")
class RFID(Resource):
    @api.response(200, "success")
    @api.response(404, "Unknown Card")
    def get(self, card_id):
        access_card = AccessCard.query.filter_by(id = card_id).first()
        if not access_card:
            return UNKNOWN_CARD_RESPONSE
        else:
            return {"user_name": access_card.user.id}



# name, email are required for new users. Ability can be passed multiple times.
# Only adds abilities; does not remove them.
@RFID_namespace.route("/update/<string:card_id>/")
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
            return CARD_UPDATE_SUCCEEDED

