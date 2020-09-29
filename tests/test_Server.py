from unittest.mock import MagicMock, patch

import pytest

from Server.NodeBlueprint import node_blueprint
from Server.Server import Server


default_property_dict = {}

known_ids = []

def getNodeAttribute(*args, **kwargs):
    if args[0] == "default":
        return default_property_dict.get(kwargs["attribute_name"])


@pytest.fixture
def app():
    with patch("dbus.SessionBus"):
        app = Server()
        app.register_blueprint(node_blueprint)
    mocked_dbus = MagicMock()
    app._nodes = mocked_dbus
    app.getMockedClient = MagicMock(return_value = mocked_dbus)
    mocked_dbus.getTemperature = MagicMock(side_effect = lambda r: getNodeAttribute(r, attribute_name ="temperature"))
    mocked_dbus.getPerformance = MagicMock(side_effect = lambda r: getNodeAttribute(r, attribute_name = "performance"))
    mocked_dbus.isNodeEnabled = MagicMock(side_effect=lambda r: getNodeAttribute(r, attribute_name= "enabled"))
    mocked_dbus.getIncomingConnections = MagicMock(side_effect=lambda r: getNodeAttribute(r, attribute_name= "incoming_connections"))
    mocked_dbus.getOutgoingConnections = MagicMock(side_effect=lambda r: getNodeAttribute(r, attribute_name="outgoing_connections"))
    mocked_dbus.getActiveModifiers= MagicMock(side_effect=lambda r: getNodeAttribute(r, attribute_name="modifiers"))
    mocked_dbus.getSurfaceArea = MagicMock(side_effect=lambda r: getNodeAttribute(r, attribute_name="surface_area"))
    mocked_dbus.getDescription = MagicMock(side_effect=lambda r: getNodeAttribute(r, attribute_name="description"))
    mocked_dbus.getTemperatureHistory = MagicMock(side_effect=lambda r: getNodeAttribute(r, attribute_name="temperature_history"))
    mocked_dbus.getAdditionalProperties = MagicMock(side_effect=lambda r: getNodeAttribute(r, attribute_name="additional_properties"))
    mocked_dbus.getMaxAdditionalPropertyValue = MagicMock(side_effect=lambda r, s: getNodeAttribute(r, attribute_name="additional_property_max")[s])
    mocked_dbus.getAdditionalPropertyValue = MagicMock(side_effect=lambda r, s: getNodeAttribute(r, attribute_name="additional_property_value")[s])
    mocked_dbus.getAdditionalPropertyHistory = MagicMock(side_effect=lambda r, s: getNodeAttribute(r, attribute_name="additional_property_history")[s])
    mocked_dbus.getAllNodeIds = MagicMock(return_value = known_ids)
    mocked_dbus.getMinPerformance = MagicMock(side_effect=lambda r: getNodeAttribute(r, attribute_name="min_performance"))
    mocked_dbus.getMaxPerformance = MagicMock(side_effect=lambda r: getNodeAttribute(r, attribute_name="max_performance"))
    mocked_dbus.getAmountStored = MagicMock(side_effect=lambda r: getNodeAttribute(r, attribute_name="amount"))
    mocked_dbus.getMaxSafeTemperature = MagicMock(side_effect=lambda r: getNodeAttribute(r, attribute_name="max_safe_temperature"))
    mocked_dbus.getHeatEmissivity = MagicMock(side_effect=lambda r: getNodeAttribute(r, attribute_name="heat_emissivity"))
    mocked_dbus.getHeatConvectionCoefficient = MagicMock(side_effect=lambda r: getNodeAttribute(r, attribute_name="heat_convection"))
    mocked_dbus.isNodeActive = MagicMock(side_effect=lambda r: getNodeAttribute(r, attribute_name="active"))
    mocked_dbus.getHistoryOffset = MagicMock(return_value = 0)
    mocked_dbus.getTargetPerformance = MagicMock(side_effect=lambda r: getNodeAttribute(r, attribute_name="target_performance"))

    return app


def test_getStaticProperties(client):
    with patch.dict(default_property_dict, {"surface_area": 20, "description": 300}):
        response = client.get("/node/default/static_properties/")
    assert response.data.strip() == b'{"surface_area": 20, "description": 300}'


def test_getModifiers(client):
    with patch.dict(default_property_dict, {"modifiers": 90001}):
        response = client.get("/node/default/modifiers/")
    assert response.data.strip() == b'90001'


def test_temperature(client):
    with patch.dict(default_property_dict, {"temperature": 9001}):
        response = client.get("/node/default/temperature/")
    assert response.data.strip() == b'9001'


def test_getIncommingConnections(client):
    with patch.dict(default_property_dict, {"incoming_connections": ["100", 300]}):
        response = client.get("/node/default/connections/incoming/")
    assert response.data.strip() == b'["100", 300]'


def test_getOutgoingConnections(client):
    with patch.dict(default_property_dict, {"outgoing_connections": [300, "100"]}):
        response = client.get("/node/default/connections/outgoing/")
    assert response.data.strip() == b'[300, "100"]'


def test_getPerformance(client):
    with patch.dict(default_property_dict, {"performance": 12}):
        response = client.get("/node/default/performance/")
    assert response.data.strip() == b'12.0'


def test_setEnabled(client):
    response = client.put("/node/default/enabled/")
    assert response.status_code == 200


def test_startTick(client):
    response = client.post("/startTick")
    client.application.getMockedClient().doTick.assert_called_once()


def test_temperatureHistory(client):
    with patch.dict(default_property_dict, {"temperature_history": [20, 30]}):
        response = client.get("/node/default/temperature/history/")
    assert response.data.strip() == b'[20, 30]'


def test_temperatureHistoryGetLast(client):
    with patch.dict(default_property_dict, {"temperature_history": [20, 30]}):
        response = client.get("/node/default/temperature/history/?showLast=1")
    assert response.data.strip() == b'[30]'

    # Check if invalid data just doesn't use the show last attribute
    with patch.dict(default_property_dict, {"temperature_history": [20, 30]}):
        response = client.get("/node/default/temperature/history/?showLast=zomg")
    assert response.data.strip() == b'[20, 30]'


def test_putPerformance(client):
    response = client.put("/node/default/performance/", data = {"performance": 200})
    assert response.status_code == 200
    client.application.getMockedClient().setTargetPerformance.assert_called_with("default", 200)


def test_getTargetPerformance(client):
    with patch.dict(default_property_dict, {"target_performance": 2}):
        response = client.get("/node/default/target_performance/")
    assert response.data.strip() == b'2'


def test_getEnabled(client):
    with patch.dict(default_property_dict, {"enabled": True}):
        response = client.get("/node/default/enabled/")
    assert response.data.strip() == b'true'


def test_getAdditionalProperties(client):
    with patch.dict(default_property_dict, {"additional_properties": ["zomg", "omg"], "additional_property_max": {"zomg": 20, "omg": 200}, "additional_property_value": {"omg": 300, "zomg": 1}}):
        response = client.get("/node/default/additional_properties/")
    assert response.status_code == 200
    assert response.data.strip() == b'{"zomg": {"max_value": 20, "value": 1}, "omg": {"max_value": 200, "value": 300}}'


def test_getUnknownNode(client):
    with patch.dict(default_property_dict, {"default": {"node_ids": []}}):
        response = client.get("/node/zomg/")

    assert response.status_code == 404


@pytest.mark.skip
def test_getAllNodeIds(client):
    client.application.getNodeData = MagicMock(return_value = {"yay": 12})
    with patch.dict(default_property_dict, {"node_ids": ["zomg", "omg"]}):
        response = client.get("/node/nodes/")
    assert response.data.strip() == b'[{"yay": 12}, {"yay": 12}]'


def test_getAdditionalPropertyValue(client):
    with patch.dict(default_property_dict, {"additional_properties": ["zomg"], "additional_property_value": {"zomg": 32}}):
        response = client.get("/node/default/zomg/")
    assert response.data.strip() == b'32'

@pytest.mark.skip()
def test_getNodeDataRequest(client):
    data = {"temperature": 200, "amount": 201, "enabled": True, "active": True, "performance": 1, "min_performance": 0.5, "max_performance": 1.5, "max_safe_temperature": 900, "heat_convection": 0.5, "heat_emissivity": 200, "surface_area": 200, "description": "THE BEST NODE"}
    with patch.dict(default_property_dict, data):
        response = client.get("/node/default/")

    assert response.data.strip() == b'{"active": true, "amount": 201, "description": "THE BEST NODE", "enabled": true, "heat_convection": 0.5, "heat_emissivity": 200, "max_performance": 1.5, "max_safe_temperature": 900, "min_performance": 0.5, "node_id": "default", "performance": 1, "surface_area": 200, "temperature": 200}'


def test_getAllProperties(client):
    data = {"additional_properties": ["zomg"],
            "additional_property_value": {"zomg": 32},
            "additional_property_history": {"zomg": [12, 30]},
            "temperature_history": [20, 21]}
    with patch.dict(default_property_dict, data):
        response = client.get("/node/default/all_property_chart_data/")

    assert response.data.strip() == b'{"offset": 0, "zomg": [12, 30], "temperature": [20, 21]}'


def test_getAdditionalPropertyHistory(client):
    data = {"additional_properties": ["zomg"],
            "additional_property_value": {"zomg": 32},
            "additional_property_history": {"zomg": [12, 30]},
            "temperature_history": [20, 21]}
    with patch.dict(default_property_dict, data):
        response = client.get("/node/default/zomg/history/")

    assert response.data.strip() == b'[12, 30]'