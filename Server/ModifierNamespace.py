from Server.Blueprint import api
from flask_restx import Resource, Api, apidoc, fields, Namespace, Model
from flask import current_app as app
modifier_namespace = Namespace("modifier", description = "Nodes can have modifiers. This API allows checking what the modifiers actually do")

modifier = api.model("modifier",
{
    "name": fields.String(description = "Human readable name of the modifier"),
    "abbreviation": fields.String(description = "Three letter abbreviation of this modifier"),
    "description": fields.String(description = "Some extra information about this modifier")
})

