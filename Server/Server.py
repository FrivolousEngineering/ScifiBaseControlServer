from typing import Optional, cast, Any, List, Dict, Union
from functools import wraps
from flask import Flask, Response, jsonify
from flask_swagger import swagger
from functools import partial
import flask
from flask import render_template, request
import json

from Server.Database import db_session
from Server.models import User, Ability
from werkzeug.exceptions import Forbidden, Unauthorized
_REGISTERED_ROUTES = {}  # type: Dict[str, Dict[str, Any]]

import dbus
import dbus.exceptions


def register_route(route: Optional[str] = None, accepted_methods: Optional[List[str]] = None):
    """
    Simple decorator for class based views. It's probably hacking a bit around the default stuff of flask...
    :param route: url it needs to listen to.
    :param accepted_methods: What methods (GET, PUT, SET) are accepted?
    :return:
    """
    def inner(function):
        result_dict = {"func": function}
        if accepted_methods is None:
            result_dict["methods"] = ["GET"]
        else:
            result_dict["methods"] = accepted_methods
        _REGISTERED_ROUTES[route] = result_dict
        return function
    return inner


def requires_user_ability(abilities: Union[str, List[str]]):
    """
    Decorator that marks a given endpoint as needing an ability (A certain right, which a user gets from a role!)
    :param abilities:
    :return:
    """
    def wrapper(func):
        @wraps(func)
        def inner(*args, **kwargs):
            user_id = request.args.get("userID")
            if not user_id:
                raise Unauthorized("You need to provide some credentials first!")
            user = User.query.filter_by(id = user_id).first()
            if not user:
                raise Forbidden("User is unknown")

            if isinstance(abilities, str):
                desired_abilities = [Ability.query.filter_by(name = abilities).first()]
            else:
                desired_abilities = Ability.query.filter(Ability.name.in_(abilities)).all()

            user_abilities = []
            for role in user.roles:
                user_abilities += role.abilities

            for desired_ability in desired_abilities:
                if desired_ability in user_abilities:
                    return func(*args, **kwargs)

            raise Forbidden("User is not allowed to do this!")

        return inner
    return wrapper


class Server(Flask):
    STATIC_LOCATION = ""
    
    def __init__(self, *args, **kwargs) -> None:
        if "import_name" not in kwargs:
            kwargs.setdefault('import_name', __name__)

        super().__init__(*args, **kwargs)

        # Register the routes from the decorator
        self.add_url_rule(rule="/<path:path>", view_func=self.staticHost)
        for route, config_options in _REGISTERED_ROUTES.items():
            partial_fn = partial(config_options["func"], self)
            # We must set a name to for this partial function.
            cast(Any, partial_fn).__name__ = config_options["func"].__name__
            self.add_url_rule(route, view_func = partial_fn, methods = config_options["methods"])

        self._bus = dbus.SessionBus()

        self.register_error_handler(dbus.exceptions.DBusException, self._dbusNotRunning)

        # This is needed for the sqlalchemy database
        self.teardown_appcontext(self._shutdownSession)

        self._nodes = None

    @staticmethod
    def _shutdownSession(exception):
        db_session.remove()

    def getDBusObject(self):
        self._setupDBUS()
        return self._nodes

    def _dbusNotRunning(self, exception: dbus.exceptions.DBusException) -> Response:
        self._nodes = None
        return Response(flask.json.dumps({"error": "DBUS Exception", "message": str(exception)}),
                        status=500,
                        mimetype="application/json")


    def _setupDBUS(self) -> None:
        self._initDBUS()
        try:
            self._nodes.checkAlive()  # type: ignore
        except dbus.exceptions.DBusException:
            self._nodes = None
            # It could be that the service was rebooted, so we should try this again.
            self._initDBUS()

    def _initDBUS(self) -> None:
        """
        Create DBUS object.
        """
        if self._nodes is None:
            try:
                self._nodes = self._bus.get_object('com.frivengi.nodes', '/com/frivengi/nodes')
            except dbus.exceptions.DBusException as exception:
                self._nodes = None
                raise exception

    def staticHost(self, path: str) -> Any:
        """
        Used for providing files that are hosted in maintenance / admin pages
        :param path:
        :return:
        """
        return flask.send_from_directory(self.STATIC_LOCATION, path)

    @register_route("/spec")
    def spec(self):
        return jsonify(swagger(self))

    @register_route("/")
    def renderStartPage(self):
        self._setupDBUS()
        display_data = []
        return render_template("index.html", data = display_data)

    @register_route("/userManagement")
    def renderUserManagementPage(self):
        return render_template("userManagement.html")


    @register_route("/users/")
    @requires_user_ability("see_users")
    def listAllUsers(self):
        all_users = User.query.all()
        return Response(flask.json.dumps([user.name for user in all_users]), status=200, mimetype="application/json")

    @register_route("/startTick", ["POST"])
    def startTick(self) -> Response:
        self._setupDBUS()
        self._nodes.doTick()  # type: ignore

        return Response(flask.json.dumps({"message": ""}), status=200, mimetype="application/json")


if __name__ == "__main__":
    Server().run(debug=True)
