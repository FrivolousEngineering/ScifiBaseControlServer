from typing import Optional

from Nodes.Modifiers.BoostCoolingModifier import BoostCoolingModifier
from Nodes.Modifiers.Modifier import Modifier
from Nodes.Modifiers.OverrideDefaultSafetyControlsModifier import OverrideDefaultSafetyControlsModifier
from Nodes.Modifiers.RepairOverTimeModifier import RepairOverTimeModifier

DEFAULT_DURATION = 10


def createModifier(modifier: str) -> Optional[Modifier]:
    if modifier == "BoostCooling":
        return BoostCoolingModifier(DEFAULT_DURATION)
    if modifier == "SafetyOverride":
        return OverrideDefaultSafetyControlsModifier(DEFAULT_DURATION)
    if modifier == "RepairOverTime":
        return RepairOverTimeModifier(2, DEFAULT_DURATION)
    return None