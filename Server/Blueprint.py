from typing import Optional, Dict, Any

from flask import Blueprint, request, Response
from flask import current_app as app
from flask_restx import Resource, Api, apidoc, fields, Namespace, Model
import json


blueprint = Blueprint('node', __name__)
api = Api(blueprint, description="This API enables access & control of this system.")



@blueprint.route('/doc/')
def swagger_ui():
    return apidoc.ui_for(api)