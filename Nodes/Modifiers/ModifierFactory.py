from typing import Optional, TYPE_CHECKING, Dict, List, cast, Any, Union

from Nodes.Modifiers.BoostCoolingModifier import BoostCoolingModifier
from Nodes.Modifiers.HeatResistantLubricationInjectionModifier import HeatResistantLubricationInjectionModifier
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
from Nodes.Modifiers.HugeHeatPackModifier import HugeHeatPackModifier
from Nodes.Modifiers.HugeCoolingPackModifier import HugeCoolingPackModifier
from Nodes.Modifiers.EmergencyShutdownModifier import EmergencyShutdownModifier
from Nodes.Modifiers.ScheduledMaintenanceModifier import ScheduledMaintenanceModifier


DEFAULT_DURATION = 10

if TYPE_CHECKING:
    from Nodes.Node import Node


class ModifierFactory:
    _supported_modifiers = {}  # type: Dict[str, List[str]]
    _all_known_modifiers = ["BoostCoolingModifier", "OverrideDefaultSafetyControlsModifier", "RepairOverTimeModifier", "JuryRigModifier",
                            "SmallHeatPackModifier", "MediumHeatPackModifier", "LargeHeatPackModifier",
                            "SmallCoolingPackModifier", "MediumCoolingPackModifier", "LargeCoolingPackModifier",
                            "PyrolythicResistantEnzymeInjectorModifier", "HeatResistantLubricationInjectionModifier",
                            "OverclockModifier", "PressureReleaseValveModifier", "HugeCoolingPackModifier",
                            "HugeHeatPackModifier", "ScheduledMaintenanceModifier", "EmergencyShutdownModifier"]

    _modifier_cache = {}  # type: Dict[str, Modifier]

    @classmethod
    def getAllKnownModifiers(cls) -> List[str]:
        return cls._all_known_modifiers.copy()

    @classmethod
    def _getModifierByType(cls, modifier_type: str) -> Optional[Modifier]:
        if modifier_type not in cls._modifier_cache:
            modifier = cls.createModifier(modifier_type)
            if not modifier:
                return None
            cls._modifier_cache[modifier_type] = modifier
        return cls._modifier_cache[modifier_type]

    @classmethod
    def getModifierInfo(cls, modifier_type: str) -> Optional[Dict[str, Union[str, int]]]:
        """
        Provide static (eg; class based, not *object* based) information about a modifier.
        :param modifier_type:
        :return:
        """
        modifier = cls._getModifierByType(modifier_type)
        if not modifier:
            return None
        return {"name": modifier.name,
                "type": modifier_type,
                "description": modifier.description,
                "required_engineering_level": modifier.required_engineering_level}

    @classmethod
    def isModifierSupported(cls, node: "Node", modifier: Modifier) -> bool:
        if modifier.required_tag is not None:
            if modifier.required_tag not in node.tags:
                return False
        if modifier.disallowed_tags:
            for tag in node.tags:
                if tag in modifier.disallowed_tags:
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
            # If no performance can be set, the min & max should also not be changeable!
            if "min_performance" in all_properties or "max_performance" in all_properties:
                if type(modifier) == ScheduledMaintenanceModifier:
                    return True
                return False
        return True

    @classmethod
    def getSupportedModifiersForNode(cls, node: "Node") -> List[str]:
        node_class_name = node.__class__.__name__
        if node_class_name not in cls._supported_modifiers:
            modifiers = []
            for modifier_type in cls._all_known_modifiers:
                if cls.isModifierSupported(node, cast(Modifier, cls._getModifierByType(modifier_type))):
                    modifiers.append(modifier_type)
            cls._supported_modifiers[node_class_name] = modifiers
        return cls._supported_modifiers[node_class_name]

    @classmethod
    def createModifier(cls, modifier: str) -> Optional[Modifier]:
        if modifier == "RepairOverTimeModifier":
            return RepairOverTimeModifier(2, DEFAULT_DURATION)
        if modifier == "JuryRigModifier":
            return JuryRigModifier(25, DEFAULT_DURATION)

        if modifier in globals() and modifier in cls._all_known_modifiers:
            modifier_class = globals()[modifier]
            return modifier_class(duration = DEFAULT_DURATION)

        return None
