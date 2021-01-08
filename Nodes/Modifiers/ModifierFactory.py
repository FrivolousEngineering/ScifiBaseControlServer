from typing import Optional, TYPE_CHECKING, Dict, List, cast

from Nodes.Modifiers.BoostCoolingModifier import BoostCoolingModifier
from Nodes.Modifiers.JuryRigModifier import JuryRigModifier
from Nodes.Modifiers.Modifier import Modifier
from Nodes.Modifiers.OverrideDefaultSafetyControlsModifier import OverrideDefaultSafetyControlsModifier
from Nodes.Modifiers.RepairOverTimeModifier import RepairOverTimeModifier

DEFAULT_DURATION = 10

if TYPE_CHECKING:
    from Node import Node


class ModifierFactory:
    _supported_modifiers = {}  # type: Dict[str, List[str]]
    _all_known_modifiers = ["BoostCoolingModifier", "OverrideDefaultSafetyControlsModifier", "RepairOverTimeModifier", "JuryRigModifier"]

    @classmethod
    def isModifierSupported(cls, node: "Node", modifier: Modifier) -> bool:
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
                if cls.isModifierSupported(node, cast(Modifier, cls.createModifier(modifier_type))):
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
        return None