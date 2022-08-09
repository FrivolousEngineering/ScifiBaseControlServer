import json

import dbus
import dbus.exceptions
import flask

from typing import Optional, cast, Any, List, Dict, TYPE_CHECKING

from functools import wraps, partial
from flask import Flask, Response, render_template, request


from Server.Database import init_db, createDBSession, getDBSession
from Server.models import User, Ability, AccessCard, Modifier
from werkzeug.exceptions import Forbidden, Unauthorized

if TYPE_CHECKING:
    from Nodes.NodesDBusService import NodesDBusService

_REGISTERED_ROUTES = {}  # type: Dict[str, Dict[str, Any]]


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


def requires_user_ability(ability: str):
    """
    Decorator that marks a given endpoint as needing an ability
    :param abilities:
    :return:
    """
    def wrapper(func):
        @wraps(func)
        def inner(*args, **kwargs):
            card_id = request.args.get("accessCardID")
            if not card_id:
                raise Unauthorized("You need to provide some credentials first!")
            access_card = AccessCard.query.filter_by(id = card_id).first()

            if not access_card:
                raise Forbidden(f"Access card [{card_id}] is unknown")

            desired_ability = Ability.query.filter_by(name = ability).first()
            user = access_card.user
            if desired_ability in user.abilities:
                return func(*args, **kwargs)

            raise Forbidden("User is not allowed to do this!")

        return inner
    return wrapper


class Server(Flask):
    """
    The server provides the REST API for the engine. It connects to the engine via DBUS. This might be seen as a bit
    of overkill, but previous projects have shown that it's good to seperate interface and business logic from oneother.

    Since the connection is via DBUS, it also means that the server and the engine can (and even need) to run in their
    own python instance. This has the added benefit that each of them has their own GIL. It should be noted that DBUS
    itself can cause calls to be blocked, so there is some waiting that can occur.

    In the future it might be needed to cache results if it turns out that the many DBUS calls cause delays, but this
    seems to not have been an issue so far.

    The server itself uses various blueprints to actually create the various API's and document them.
    """

    STATIC_LOCATION = ""
    
    def __init__(self, db_location: str, *args, **kwargs) -> None:
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

        self.register_error_handler(dbus.exceptions.DBusException, self._dbusExceptionHandler)  # type: ignore

        # This is needed for the sqlalchemy database
        self.teardown_appcontext(self._shutdownSession)

        self._nodes = None  # type: Optional["NodesDBusService"]
        self._modifiers = None
        self._last_known_tick = 0

        createDBSession(db_location)
        init_db()

    @staticmethod
    def _shutdownSession(exception):
        getDBSession().remove()

    def getNodeDBusObject(self) -> "NodesDBusService":
        """
        Convenience function that ensures that the dbus connection is setup.

        It can raise dbus.exceptions.DBusException if it was not able to set it up.
        :return:
        """
        self._setupNodeDBUS()
        return cast("NodesDBusService", self._nodes)

    def getModifierDBusObject(self):
        self._setupModifierDBUS()
        return self._modifiers

    def _setupModifierDBUS(self) -> None:
        self._initModifierDBUS()
        try:
            self._modifiers.checkAlive()  # type: ignore
        except dbus.exceptions.DBusException:
            self._modifiers = None
            # It could be that the service was rebooted, so we should try this again.
            self._initModifierDBUS()

    def _initModifierDBUS(self) -> None:
        """
        Create DBUS object for the nodes.
        """
        if self._modifiers is None:
            try:
                self._modifiers = self._bus.get_object('com.frivengi.modifiers', '/com/frivengi/modifiers')
            except dbus.exceptions.DBusException as exception:
                self._modifiers = None
                raise exception

    def _dbusExceptionHandler(self, exception: dbus.exceptions.DBusException) -> Response:
        if exception.get_dbus_name() == "org.freedesktop.DBus.Error.ServiceUnknown":
            # We couldn't find the server on the other side. No need to log it more
            self._nodes = None
            return Response('{"message": "The engine cant be found. Ensure that its running before trying again"}',
                            status = 503,
                            mimetype="application/json")
        else:
            self.logger.warning("An exception occurred %s" % str(exception))
        return Response('{"message": "An exception ocurred: ' + str(exception) + '"}',
                        status=500,
                        mimetype="application/json")

    def _handleTickUpdate(self) -> None:
        try:
            for modifier in Modifier.query.all():
                # Check if the modifier has been removed.
                modifier_names = [mod["type"] for mod in self._nodes.getActiveModifiers(modifier.node_id)]  # type: ignore

                if modifier.name not in modifier_names:
                    getDBSession().delete(modifier)  # type: ignore
            getDBSession().commit()  # type: ignore

        except Exception as e:
            print(e)

    def _setupNodeDBUS(self) -> None:
        self._initNodeDBUS()
        try:
            self._nodes.checkAlive()  # type: ignore
            # Since getting DBUS signals to work properly with flask proved to be annoying, we just use ask what the
            # last tick that we saw was. Based on that we can decide if an update is needed.
            # Since this function is always called before any update, we should never get outdated info.
            tick_number = self._nodes.getCurrentTick()  # type: ignore
            if self._last_known_tick != tick_number:
                self._last_known_tick = tick_number
                self._handleTickUpdate()

        except dbus.exceptions.DBusException:
            self._nodes = None
            # It could be that the service was rebooted, so we should try this again.
            self._initNodeDBUS()
        except AttributeError:
            self._nodes = None
            self._initNodeDBUS()

    def _initNodeDBUS(self) -> None:
        """
        Create DBUS object for the nodes.
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

    @register_route("/")
    def renderStartPage(self):
        try:
            self._setupNodeDBUS()
        except dbus.exceptions.DBusException:
            pass
        display_data = []
        return render_template("index.html", data = display_data)

    @register_route("/userManagement")
    def renderUserManagementPage(self):
        return render_template("userManagement.html")

    @register_route("/controllerManagement")
    def renderControllerManagementPage(self):
        return render_template("controllerManagement.html")

    @register_route("/users/")
    @requires_user_ability("see_users")
    def listAllUsers(self):
        all_users = User.query.all()
        return Response(flask.json.dumps([user.id for user in all_users]), status=200, mimetype="application/json")

    @register_route("/tick_interval", ["put"])
    def setTickInterval(self) -> Response:
        self._setupNodeDBUS()

        data = json.loads(request.data)
        self._nodes.setTickInterval(data["value"])

        return Response(flask.json.dumps({"message": ""}), status=200, mimetype="application/json")

    @register_route("/paused", ["get"])
    def isPaused(self) -> Response:
        self._setupNodeDBUS()

        return Response(str(bool(self._nodes.isPaused())), status=200) # type:ignore

    @register_route("/pause", ["POST"])
    def pauseTickTimer(self) -> Response:
        self._setupNodeDBUS()
        self._nodes.stopEngineTimer()  # type: ignore

        return Response(flask.json.dumps({"message": ""}), status=200, mimetype="application/json")

    @register_route("/start", ["POST"])
    def runTickTimer(self) -> Response:
        self._setupNodeDBUS()
        self._nodes.startEngineTimer()  # type: ignore

        return Response(flask.json.dumps({"message": ""}), status=200, mimetype="application/json")

    @register_route("/startTick", ["POST"])
    def startTick(self) -> Response:
        self._setupNodeDBUS()
        self._nodes.doTick()  # type: ignore

        return Response(flask.json.dumps({"message": ""}), status=200, mimetype="application/json")




if __name__ == "__main__":
    Server('sqlite:///ScifiControlServer.db').run(debug=True)
