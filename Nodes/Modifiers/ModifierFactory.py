from typing import Optional, TYPE_CHECKING, Dict, List, cast

from Nodes.Modifiers.BoostCoolingModifier import BoostCoolingModifier
from Nodes.Modifiers.HeatResistantLubricationInjectionModifier import HeatResistantLubricationInjection
from Nodes.Modifiers.JuryRigModifier import JuryRigModifier
from Nodes.Modifiers.LargeCoolingPack import LargeCoolingPackModifier
from Nodes.Modifiers.LargeHeatPackModifier import LargeHeatPackModifier
from Nodes.Modifiers.MediumCoolingPackModifier import MediumCoolingPackModifier
from Nodes.Modifiers.MediumHeatPack import MediumHeatPackModifier
from Nodes.Modifiers.Modifier import Modifier
from Nodes.Modifiers.OverclockModifier import OverclockModifier
from Nodes.Modifiers.OverrideDefaultSafetyControlsModifier import OverrideDefaultSafetyControlsModifier
from Nodes.Modifiers.PressureReleaseValveModifier import PressureReleaseValveModifier
from Nodes.Modifiers.PyrolythicRestistantEnzymeInjectorModifier import PyrolythicResistantEnzymeInjectorModifier
from Nodes.Modifiers.RepairOverTimeModifier import RepairOverTimeModifier
from Nodes.Modifiers.SmallCoolingPackModifier import SmallCoolingPackModifier
from Nodes.Modifiers.SmallHeatPackModifier import SmallHeatPackModifier

DEFAULT_DURATION = 10

if TYPE_CHECKING:
    from Node import Node


class ModifierFactory:
    _supported_modifiers = {}  # type: Dict[str, List[str]]
    _all_known_modifiers = ["BoostCoolingModifier", "OverrideDefaultSafetyControlsModifier", "RepairOverTimeModifier", "JuryRigModifier",
                            "SmallHeatPackModifier", "MediumHeatPackModifier", "LargeHeatPackModifier",
                            "SmallCoolingPackModifier", "MediumCoolingPackModifier", "LargeCoolingPackModifier",
                            "PyrolythicResistantEnzymeInjectorModifier", "HeatResistantLubricationInjectionModifier",
                            "OverclockModifier", "PressureReleaseValveModifier"]

    _modifier_cache = {}  # type: Dict[str, Modifier]

    @classmethod
    def isModifierSupported(cls, node: "Node", modifier: Modifier) -> bool:
        if modifier.required_tag is not None:
            if modifier.required_tag not in node.tags:
                return False

        if modifier.optional_tags:
            optional_tag_matched = False
            for tag in node.tags:
                if tag in modifier.optional_tags:
                    optional_tag_matched = True
                    break

            if not optional_tag_matched:
                return False

        all_properties = modifier.getAllInfluencedProperties()
        if not node.hasSettablePerformance:
            # If no performance can be set, the min & max should also not be changable!
            if "min_performance" in all_properties or "max_performance" in all_properties:
                return False
        return True

    @classmethod
    def getSupportedModifiersForNode(cls, node: "Node") -> List[str]:
        node_class_name = node.__class__.__name__
        if node_class_name not in cls._supported_modifiers:
            modifiers = []
            for modifier_type in cls._all_known_modifiers:
                if modifier_type not in cls._modifier_cache:
                    cls._modifier_cache[modifier_type] = cls.createModifier(modifier_type)
                if cls.isModifierSupported(node, cast(Modifier, cls._modifier_cache[modifier_type])):
                    modifiers.append(modifier_type)
            cls._supported_modifiers[node_class_name] = modifiers
        return cls._supported_modifiers[node_class_name]

    @classmethod
    def createModifier(cls, modifier: str) -> Optional[Modifier]:
        if modifier == "BoostCoolingModifier":
            return BoostCoolingModifier(DEFAULT_DURATION)
        if modifier == "OverrideDefaultSafetyControlsModifier":
            return OverrideDefaultSafetyControlsModifier(DEFAULT_DURATION)
        if modifier == "RepairOverTimeModifier":
            return RepairOverTimeModifier(2, DEFAULT_DURATION)
        if modifier == "JuryRigModifier":
            return JuryRigModifier(25, DEFAULT_DURATION)

        if modifier == "SmallHeatPackModifier":
            return SmallHeatPackModifier(DEFAULT_DURATION)
        if modifier == "MediumHeatPackModifier":
            return MediumHeatPackModifier(DEFAULT_DURATION)
        if modifier == "LargeHeatPackModifier":
            return LargeHeatPackModifier(DEFAULT_DURATION)

        if modifier == "SmallCoolingPackModifier":
            return SmallCoolingPackModifier(DEFAULT_DURATION)
        if modifier == "MediumCoolingPackModifier":
            return MediumCoolingPackModifier(DEFAULT_DURATION)
        if modifier == "LargeCoolingPackModifier":
            return LargeCoolingPackModifier(DEFAULT_DURATION)

        if modifier == "PyrolythicResistantEnzymeInjectorModifier":
            return PyrolythicResistantEnzymeInjectorModifier(DEFAULT_DURATION)

        if modifier == "HeatResistantLubricationInjectionModifier":
            return HeatResistantLubricationInjection(DEFAULT_DURATION)

        if modifier == "OverclockModifier":
            return OverclockModifier(DEFAULT_DURATION)

        if modifier == "PressureReleaseValveModifier":
            return PressureReleaseValveModifier(DEFAULT_DURATION)
        return None