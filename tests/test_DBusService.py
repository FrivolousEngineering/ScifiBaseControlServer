from unittest.mock import MagicMock, patch

import pytest

from Nodes.Node import Node
from Nodes.DBusService import DBusService
from Nodes.NodeEngine import NodeEngine


node_dict = {}


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
                                              ("max_performance", 1.3)])
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
                                              ("max_performance", 1)])
def test_getAttributeValueUnknownNode(DBus, node, attribute, value):
    setattr(node, attribute, value)

    func_name = attribute.title()  # ensure right casing.
    func_name = func_name.replace("_", "")  # Remove all the underscores
    func_name = "get" + func_name  # And finally, add a get.

    with patch.dict(node_dict, {"zomg": node}):
        assert getattr(DBus, func_name)("SomethingDifferent!") == value


def test_setPerformance(DBus, node):
    with patch.dict(node_dict, {"zomg": node}):
        DBus.setPerformance("zomg", 2000)
        assert node.performance == 2000