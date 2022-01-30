import pytest

from Nodes.Modifiers.ModifierFactory import ModifierFactory


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