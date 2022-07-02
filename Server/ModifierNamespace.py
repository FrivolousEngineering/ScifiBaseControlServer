from Nodes.Modifiers.ModifierFactory import ModifierFactory
from Server.Blueprint import api
from flask_restx import Resource, Api, apidoc, fields, Namespace, Model
from flask import current_app as app
modifier_namespace = Namespace("modifier", description = "Nodes can have modifiers. This API allows checking what the modifiers actually do")

modifier = api.model("modifier",
{
    "name": fields.String(description = "Human readable name of the modifier"),
    "type": fields.String(description = "The not human readable type of the modifier", enum = ModifierFactory._all_known_modifiers),
    "abbreviation": fields.String(description = "Three letter abbreviation of this modifier"),
    "description": fields.String(description = "Some extra information about this modifier"),
})


@modifier_namespace.route("/")
@modifier_namespace.doc(description = "Get all modifier types")
class Modifiers(Resource):
    @api.response(200, "Success", fields.List(fields.Nested(modifier)))
    def get(self):
        modifiers = app.getModifierDBusObject()
        if modifiers:
            all_known_modifiers = modifiers.getAllKnownModifiers()
            result = []
            for modifier_type in all_known_modifiers:
                result.append(modifiers.getModifierInformation(modifier_type))
            return result
        return []

