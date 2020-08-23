from unittest.mock import MagicMock, patch

import pytest

from Nodes.Node import Node
from Nodes.DBusService import DBusService
from Nodes.NodeEngine import NodeEngine


node_dict = {}

node_history_dict = {}


@pytest.fixture
def node():
    mock_node = MagicMock(spec = Node)
    return mock_node


@pytest.fixture
def session_bus():
    session_bus = MagicMock(name="mocked_session_bus")
    return session_bus


@pytest.fixture
def node_engine():
    node_engine = MagicMock(spec=NodeEngine)
    node_engine.getNodeById = MagicMock(side_effect = lambda r: node_dict.get(r))
    node_engine.getNodeHistoryById = MagicMock(side_effect = lambda r: node_history_dict.get(r))
    return node_engine


@pytest.fixture
def bus_name():
    bus_name = MagicMock(name="mocked_session_bus")
    return bus_name


@pytest.fixture
def DBus(session_bus, bus_name, node_engine):
    service = DBusService(node_engine, session_bus = session_bus, bus_name = bus_name)
    service.getNodeEngine = MagicMock(return_value = node_engine)
    return service


def test_getUnknownNodeTemperature(DBus):
    assert DBus.getTemperature("zomg") == -9000


@pytest.mark.parametrize("attribute, value", [("temperature", 2000),
                                              ("description", "omgzomg"),
                                              ("heat_emissivity", 200),
                                              ("surface_area", 300),
                                              ("heat_convection_coefficient", 42),
                                              ("max_safe_temperature", 2000),
                                              ("performance", 2),
                                              ("additional_properties", ["omg", "woah!", "panda"]),
                                              ("amount_stored", 17),
                                              ("min_performance", 0.2),
                                              ("max_performance", 1.3),
                                              ("target_performance", 0.2)])
def test_getAttributeValue(DBus, node, attribute, value):
    setattr(node, attribute, value)

    func_name = attribute.title()  # ensure right casing.
    func_name = func_name.replace("_", "")  # Remove all the underscores
    func_name = "get" + func_name  # And finally, add a get.

    with patch.dict(node_dict, {"zomg": node}):
        assert getattr(DBus, func_name)("zomg") == value


@pytest.mark.parametrize("attribute, value", [("temperature", -9000),
                                              ("description", ""),
                                              ("heat_emissivity", 0),
                                              ("surface_area", 0),
                                              ("heat_convection_coefficient", 0),
                                              ("max_safe_temperature", 0),
                                              ("performance", 0),
                                              ("additional_properties", []),
                                              ("amount_stored", -1),
                                              ("min_performance", 1),
                                              ("max_performance", 1),
                                              ("target_performance", 0)])
def test_getAttributeValueUnknownNode(DBus, node, attribute, value):
    setattr(node, attribute, value)

    func_name = attribute.title()  # ensure right casing.
    func_name = func_name.replace("_", "")  # Remove all the underscores
    func_name = "get" + func_name  # And finally, add a get.

    with patch.dict(node_dict, {"zomg": node}):
        assert getattr(DBus, func_name)("SomethingDifferent!") == value


def test_setPerformance(DBus, node):
    with patch.dict(node_dict, {"zomg": node}):
        DBus.setTargetPerformance("zomg", 2000)
        assert node.target_performance == 2000


def test_isNodeActive(DBus):
    inactive_node = MagicMock(active = False)
    active_node = MagicMock(active = True)
    with patch.dict(node_dict, {"inactive_node": inactive_node, "active_node": active_node}):
        assert DBus.isNodeActive("active_node")
        assert not DBus.isNodeActive("inactive_node")
        assert not DBus.isNodeActive("unknown_node")


def test_getTemperatureHistory(DBus):
    history = MagicMock(getTemperatureHistory = MagicMock(return_value = [10, 20, 21]))

    with patch.dict(node_history_dict, {"zomg": history}):
        assert DBus.getTemperatureHistory("zomg") == [10, 20, 21]
        assert DBus.getTemperatureHistory("whoo") == []


def test_getAdditionalPropertyHistory(DBus):
    history = MagicMock(getAdditionalPropertiesHistory = MagicMock(return_value = {"yay" : [10, 20, 21]}))

    with patch.dict(node_history_dict, {"zomg": history}):
        assert DBus.getAdditionalPropertyHistory("zomg", "yay") == [10, 20, 21]
        assert DBus.getAdditionalPropertyHistory("zomg", "nope") == []
        assert DBus.getAdditionalPropertyHistory("whoo", "yay") == []


def test_addModifierToNode(DBus):
    mod_node = MagicMock()
    modifier = MagicMock()
    modifier_func = MagicMock(return_value = modifier, name ="mod func")
    with patch("Nodes.DBusService.createModifier", modifier_func):
        with patch.dict(node_dict, {"to_be_modified_node": mod_node}):
            DBus.addModifierToNode("to_be_modified_node", "yay")
    modifier_func.assert_called_once_with("yay")
    mod_node.addModifier.assert_called_once_with(modifier)


def test_getActiveModifiers(DBus):
    mod_node = MagicMock()
    unmodded_node = MagicMock()

    modifier = MagicMock(duration = 200)
    modifier.name = "modifier"  # Can't set that directly in constructor, since magicMock uses name itself
    mod_node.getModifiers = MagicMock(return_value=[modifier])
    unmodded_node.getModifiers = MagicMock(return_value = [])
    with patch.dict(node_dict, {"modded_node": mod_node, "unmodded_node": unmodded_node}):
        assert DBus.getActiveModifiers("modded_node") == [{"name": "modifier", "duration": 200}]
        assert DBus.getActiveModifiers("unmodded_node") == []
        assert DBus.getActiveModifiers("unknown_node") == []


def test_isNodeEnabled(DBus):
    node = MagicMock(enabled = True)
    disabled_node = MagicMock(enabled = False)
    with patch.dict(node_dict, {"node": node, "disabled_node": disabled_node}):
        assert DBus.isNodeEnabled("node")
        assert not DBus.isNodeEnabled("disabled_node")
        assert not DBus.isNodeEnabled("unknown_node")
