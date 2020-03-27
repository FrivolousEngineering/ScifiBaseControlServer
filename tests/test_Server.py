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
    app.getMockedClient = MagicMock(return_value = mocked_dbus)
    mocked_dbus.getNodeTemperature = MagicMock(side_effect = lambda r: getNodeAttribute(r, attribute_name = "temperature"))
    mocked_dbus.getPerformance = MagicMock(side_effect = lambda r: getNodeAttribute(r, attribute_name = "performance"))
    mocked_dbus.isNodeEnabled = MagicMock(side_effect=lambda r: getNodeAttribute(r, attribute_name= "enabled"))
    mocked_dbus.getIncomingConnections = MagicMock(side_effect=lambda r: getNodeAttribute(r, attribute_name= "incoming_connections"))
    mocked_dbus.getOutgoingConnections = MagicMock(side_effect=lambda r: getNodeAttribute(r, attribute_name="outgoing_connections"))
    mocked_dbus.getActiveModifiers= MagicMock(side_effect=lambda r: getNodeAttribute(r, attribute_name="modifiers"))
    mocked_dbus.getSurfaceArea = MagicMock(side_effect=lambda r: getNodeAttribute(r, attribute_name="surface_area"))
    mocked_dbus.getNodeDescription = MagicMock(side_effect=lambda r: getNodeAttribute(r, attribute_name="description"))
    mocked_dbus.getNodeTemperatureHistory = MagicMock(side_effect=lambda r: getNodeAttribute(r, attribute_name="temperature_history"))
    mocked_dbus.getAdditionalProperties = MagicMock(side_effect=lambda r: getNodeAttribute(r, attribute_name="additional_properties"))
    mocked_dbus.getMaxAdditionalPropertyValue = MagicMock(side_effect=lambda r, s: getNodeAttribute(r, attribute_name="additional_property_max")[s])
    mocked_dbus.getAdditionalPropertyValue = MagicMock(side_effect=lambda r, s: getNodeAttribute(r, attribute_name="additional_property_value")[s])
    mocked_dbus.getAllNodeIds = MagicMock(side_effect=lambda : getNodeAttribute("default", attribute_name="node_ids"))
    return app


def test_getStaticProperties(client):
    with patch.dict(default_property_dict, {"surface_area": 20, "description": 300}):
        response = client.get("/default/static_properties")
    assert response.data == b'{"description": 300, "surface_area": 20}'


def test_getModifiers(client):
    with patch.dict(default_property_dict, {"modifiers": 90001}):
        response = client.get("/default/modifiers")
    assert response.data == b'90001'


def test_temperature(client):
    with patch.dict(default_property_dict, {"temperature": 9001}):
        response = client.get("/default/temperature/")
    assert response.data == b'9001'


def test_getIncommingConnections(client):
    with patch.dict(default_property_dict, {"incoming_connections": ["100", 300]}):
        response = client.get("/default/connections/incoming")
    assert response.data == b'["100", 300]'


def test_getOutgoingConnections(client):
    with patch.dict(default_property_dict, {"outgoing_connections": [300, "100"]}):
        response = client.get("/default/connections/outgoing")
    assert response.data == b'[300, "100"]'


def test_getPerformance(client):
    with patch.dict(default_property_dict, {"performance": 12}):
        response = client.get("/default/performance/")
    assert response.data == b'12'


def test_setEnabled(client):
    response = client.put("/default/enabled/")
    assert response.status_code == 200


def test_startTick(client):
    response = client.post("/startTick")
    client.application.getMockedClient().doTick.assert_called_once()


def test_temperatureHistory(client):
    with patch.dict(default_property_dict, {"temperature_history": [20, 30]}):
        response = client.get("/default/temperature/history/")
    assert response.data == b'[20, 30]'


def test_temperatureHistoryGetLast(client):
    with patch.dict(default_property_dict, {"temperature_history": [20, 30]}):
        response = client.get("/default/temperature/history/?showLast=1")
    assert response.data == b'[30]'

    # Check if invalid data just doesn't use the show last attribute
    with patch.dict(default_property_dict, {"temperature_history": [20, 30]}):
        response = client.get("/default/temperature/history/?showLast=zomg")
    assert response.data == b'[20, 30]'


def test_putPerformance(client):
    response = client.put("/default/performance/", data = {"performance": 200})
    assert response.status_code == 200
    client.application.getMockedClient().setPerformance.assert_called_with("default", 200)


def test_getEnabled(client):
    with patch.dict(default_property_dict, {"enabled": True}):
        response = client.get("/default/enabled/")
    assert response.data == b'true'


def test_getAdditionalProperties(client):
    with patch.dict(default_property_dict, {"additional_properties": ["zomg", "omg"], "additional_property_max": {"zomg": 20, "omg": 200}, "additional_property_value": {"omg": 300, "zomg": 1}}):
        response = client.get("/default/additional_properties")
    assert response.status_code == 200
    assert response.data == b'{"omg": {"max_value": 200, "value": 300}, "zomg": {"max_value": 20, "value": 1}}'


def test_getAllNodeIds(client):
    client.application.getNodeData = MagicMock(return_value = {"yay": 12})
    with patch.dict(default_property_dict, {"node_ids": ["zomg", "omg"]}):
        response = client.get("/nodes/")
    assert response.data == b'[{"yay": 12}, {"yay": 12}]'


def test_getAdditionalPropertyValue(client):
    with patch.dict(default_property_dict, {"additional_properties": ["zomg"], "additional_property_value": {"zomg": 32}}):
        response = client.get("/default/zomg/")
    assert response.data == b'32'