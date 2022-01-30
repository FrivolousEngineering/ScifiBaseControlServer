from unittest.mock import MagicMock

import pytest

from Nodes.Modifiers.Modifier import Modifier
from Nodes.Modifiers.ModifierFactory import ModifierFactory
from Nodes.Node import Node

all_known_modifiers = ["BoostCoolingModifier", "OverrideDefaultSafetyControlsModifier", "RepairOverTimeModifier", "JuryRigModifier",
                            "SmallHeatPackModifier", "MediumHeatPackModifier", "LargeHeatPackModifier",
                            "SmallCoolingPackModifier", "MediumCoolingPackModifier", "LargeCoolingPackModifier",
                            "PyrolythicResistantEnzymeInjectorModifier", "HeatResistantLubricationInjectionModifier",
                            "OverclockModifier", "PressureReleaseValveModifier"]


@pytest.mark.parametrize("modifier_type", all_known_modifiers)
def test_getModifierByType(modifier_type):
    result = ModifierFactory._getModifierByType(modifier_type)
    assert result.__class__.__name__ == modifier_type


@pytest.mark.parametrize("modifier_type", ["omg", "dict", "object", "Node", "pytest"])
def test_getModifierByInvalidType(modifier_type):
    assert ModifierFactory._getModifierByType(modifier_type) is None


def test_isModifierSupported_requiredTagNotCorrect():
    test_node = MagicMock(spec = Node, tags = ["some_tag"])
    test_modifier = MagicMock(spec = Modifier, required_tag = "some_other_tag", optional_tags = [])

    assert not ModifierFactory.isModifierSupported(test_node, test_modifier)


def test_isModifierSupported():
    test_node = MagicMock(spec = Node, tags = ["some_tag"])
    test_modifier = MagicMock(spec = Modifier, required_tag = "some_tag", optional_tags = [])

    assert ModifierFactory.isModifierSupported(test_node, test_modifier)


def test_isModifierSupported_optionalTagNotCorrect():
    test_node = MagicMock(spec = Node, tags = ["some_tag"])
    test_modifier = MagicMock(spec = Modifier, required_tag = "some_tag", optional_tags = ["omg"])

    assert not ModifierFactory.isModifierSupported(test_node, test_modifier)


def test_isModifierSupported_optionalTagCorrect():
    test_node = MagicMock(spec = Node, tags = ["some_tag", "some_optional_tag", "some_other_tag"])
    test_modifier = MagicMock(spec = Modifier, required_tag = "some_tag", optional_tags = ["some_optional_tag"])

    assert ModifierFactory.isModifierSupported(test_node, test_modifier)


def test_isModifierSupported_settablePerformance():
    test_node = MagicMock(spec=Node, tags=["some_tag"], hasSettablePerformance = False)
    test_modifier = MagicMock(spec=Modifier, required_tag="some_tag", optional_tags=[], getAllInfluencedProperties = MagicMock(return_value=["min_performance"]))

    assert not ModifierFactory.isModifierSupported(test_node, test_modifier)