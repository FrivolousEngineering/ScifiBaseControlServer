from typing import Dict, Any


class Role:
    def __init__(self, role_type: str, level: int) -> None:
        self._type = role_type
        self._level = level

    @property
    def type(self) -> str:
        return self._type

    def serialize(self) -> Dict[str, Any]:
        result = dict()  # type: Dict[str, Any]
        result["type"] = self._type
        result["level"] = self._level
        return result

    def deserialize(self, data: Dict[str, Any]) -> None:
        self._type = data["type"]
        self._level = data["level"]

    @classmethod
    def createFromSerialized(cls, data: Dict[str, Any]) -> "Role":
        return Role(data["type"], data["level"])
