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
    assert DBus.getNodeTemperature("zomg") == -9000

@pytest.mark.parametrize("attribute, value", [("temperature", 2000),
                                              ("description", "omgzomg")])
def test_getNodeTemperature(DBus, node, attribute, value):
    setattr(node, attribute, value)

    func_name = list(attribute)
    func_name[0] = func_name[0].capitalize()
    func_name = "".join(func_name)
    func_name = "getNode" + func_name

    with patch.dict(node_dict, {"zomg": node}):
        assert getattr(DBus, func_name)("zomg") == value
