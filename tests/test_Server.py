from unittest.mock import MagicMock, patch

import pytest
from Nodes.Server import Server


default_property_dict = {}


def getNodeAttribute(*args, **kwargs):
    if args[0] == "default":
        return default_property_dict.get(kwargs["attribute_name"])


@pytest.fixture
def app():
    with patch("dbus.SessionBus"):
        app = Server()
    mocked_dbus = MagicMock()
    app._nodes = mocked_dbus
    mocked_dbus.getNodeTemperature = MagicMock(side_effect = lambda r: getNodeAttribute(r, attribute_name = "temperature"))
    mocked_dbus.getPerformance = MagicMock(side_effect = lambda r: getNodeAttribute(r, attribute_name = "performance"))
    mocked_dbus.isNodeEnabled = MagicMock(side_effect=lambda r: getNodeAttribute(r, attribute_name= "enabled"))
    return app


def test_temperature(client):
    with patch.dict(default_property_dict, {"temperature": 9001}):
        response = client.get("/default/temperature/")
    assert response.data == b'9001'


def test_performance(client):
    with patch.dict(default_property_dict, {"performance": 12}):
        response = client.get("/default/performance/")
    assert response.data == b'12'


def test_enabled(client):
    with patch.dict(default_property_dict, {"enabled": True}):
        response = client.get("/default/enabled/")
    assert response.data == b'true'