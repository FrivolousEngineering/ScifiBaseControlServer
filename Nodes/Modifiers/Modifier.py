from typing import Optional, TYPE_CHECKING, Dict, Any, Set, List

if TYPE_CHECKING:
    from Node import Node


class Modifier:
    def __init__(self, modifiers: Optional[Dict[str, float]] = None, factors:  Optional[Dict[str, float]] = None,
                 duration: int = 0) -> None:
        """
        A modifier is a (temporariy) modifier to one or more attributes of a node. Only attributes that have the
        'modifiable_property' decorator can be modified in this way. Two types of modification can be done. Adding (or
        subtracting), which is done with modifiers property. You can also use factors, which work as multipliers.

        :param modifiers: Dict with keys to indicate which property it should modify (by adding the value to the
        original)
        :param factors: Dict with keys to indicate which property it should modify (by multiplying the original
        with the value)
        :param duration: The duration this modifier will active, measured in ticks.
        """
        self._node = None  # type: Optional["Node"]

        self._duration = duration

        self._modifiers = {}  # type: Dict[str, float]
        if modifiers is not None:
            self._modifiers = modifiers

        self._factors = {}  # type: Dict[str, float]
        if factors is not None:
            self._factors = factors

        self._name = "Modifier"
        self._abbreviation = "UNK"

        # If this is set it can only be added to a node that also has this tag.
        self._required_tag = None  # type: Optional[str]

        self._optional_tags = []  # type: List[str]

        self._disallowed_tags = [] # type: List[str]

        self._description = ""
        self._required_engineering_level = 1

    @property
    def description(self) -> str:
        return self._description

    @property
    def required_tag(self) -> Optional[str]:
        return self._required_tag

    @property
    def disallowed_tags(self) -> List[str]:
        return self._disallowed_tags

    @property
    def optional_tags(self) -> List[str]:
        return self._optional_tags

    @property
    def required_engineering_level(self) -> int:
        return self._required_engineering_level

    def __eq__(self, other) -> bool:
        if type(self) != type(other):
            return False

        if self.duration != other.duration:
            return False

        if self._modifiers != other._modifiers:
            return False
        if self._factors != other._factors:
            return False
        return True

    def serialize(self) -> Dict[str, Any]:
        data = {}  # type: Dict[str, Any]
        data["type"] = type(self).__name__
        data["modifiers"] = self._modifiers
        data["factors"] = self._factors
        data["duration"] = self._duration
        return data

    def deserialize(self, data: Dict[str, Any]) -> None:
        self._modifiers = data["modifiers"]
        self._factors = data["factors"]
        self._duration = data["duration"]

    @property
    def duration(self) -> int:
        return self._duration

    @property
    def name(self) -> str:
        return self._name

    @property
    def abbreviation(self) -> str:
        return self._abbreviation

    def setNode(self, node: "Node") -> None:
        self._node = node
        self._onModifierAdded()

    def getNode(self) -> Optional["Node"]:
        return self._node

    def getModifierForProperty(self, prop: str) -> float:
        return self._modifiers.get(prop, 0.)

    def getFactorForProperty(self, prop: str) -> float:
        return self._factors.get(prop, 1)

    def getAllInfluencedProperties(self) -> Set[str]:
        result = set()  # type: Set[str]
        result.update(self._modifiers.keys())
        result.update(self._factors.keys())
        return result

    def update(self) -> None:
        self._duration -= 1
        if self._duration <= 0 and self._node is not None:
            self._node.removeModifier(self)
            self._onModifierRemoved()

    def _onModifierRemoved(self) -> None:
        pass

    def _onModifierAdded(self) -> None:
        pass