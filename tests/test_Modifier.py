from unittest.mock import MagicMock

import pytest

from Nodes.Modifiers import Modifier
from Nodes import Node


@pytest.mark.parametrize("""
mod_1,                          mod_2,                              result""",[
(Modifier.Modifier(),           None,                               False),
(Modifier.Modifier(),           Modifier.Modifier(duration = 12),   False),
(Modifier.Modifier(
    modifiers = {"omg": 12}),   Modifier.Modifier(),                False),
(Modifier.Modifier(
    factors = {"omg": 12}),     Modifier.Modifier(),                False),
(Modifier.Modifier(),            Modifier.Modifier(),                True)])
def test_compare(mod_1, mod_2, result):
    assert (mod_1 == mod_2) == result


def test_name():
    assert Modifier.Modifier().name == "Modifier"


def test_getSetNode():
    mod = Modifier.Modifier()
    mock_node = MagicMock(spec = Node.Node)
    mod.setNode(mock_node)
    assert mod.getNode() == mock_node


def test_durationRemoved():
    # A mod with a duration of 1 should be removed after a single update is done
    modifier = Modifier.Modifier(duration = 1)

    mock_node = MagicMock(spec=Node.Node)
    modifier.setNode(mock_node)

    modifier.update()

    mock_node.removeModifier.assert_called_with(modifier)
    assert modifier.duration == 0


def test_durationNotRemoved():
    modifier = Modifier.Modifier(duration=2)

    mock_node = MagicMock(spec=Node.Node)
    modifier.setNode(mock_node)

    modifier.update()

    mock_node.removeModifier.assert_not_called()
    assert modifier.duration == 1


def test_getModifierForProperty():
    mod = Modifier.Modifier(modifiers={"omg": 12})
    assert mod.getModifierForProperty("omg") == 12
    assert mod.getModifierForProperty("lol") == 0


def test_getFactorForProperty():
    mod = Modifier.Modifier(factors={"whoo": 12})
    assert mod.getFactorForProperty("whoo") == 12
    assert mod.getFactorForProperty("lol") == 1


@pytest.mark.parametrize("""
modifiers, factors, all_properties""", [
    ({"omg": 11}, None, {"omg"}),
    (None, {"omg": 90}, {"omg"}),
    ({"omg": 200}, {"omg": 10}, {"omg"}),
    ({"omg": 11, "zomg": 10}, None, {"omg", "zomg"}),
    (None, None, set()),
    (None, {"omg": 22, "zomg": 10}, {"omg", "zomg"}),
    ({"omg": 1, "zomg": 10}, {"omg": 0, "zomg": 20}, {"omg", "zomg"})
])
def test_getModifiedProperties(modifiers, factors, all_properties):
    modifier = Modifier.Modifier(modifiers = modifiers, factors = factors)
    assert modifier.getAllInfluencedProperties() == all_properties


def test_serialiseDeserialize():
    mod = Modifier.Modifier(factors={"blorp": 1000})
    second_mod = Modifier.Modifier()

    # The modifiers start off as different
    assert mod != second_mod

    data = mod.serialize()
    second_mod.deserialize(data)

    assert mod == second_mod


