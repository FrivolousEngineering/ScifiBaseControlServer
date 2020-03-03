from typing import Dict, Any


class Role:
    def __init__(self, identifier: str, level: int) -> None:
        self._id = identifier
        self._level = level

    @property
    def id(self) -> str:  # pylint: disable=C0103
        return self._id

    def serialize(self) -> Dict[str, Any]:
        result = dict()  # type: Dict[str, Any]
        result["id"] = self._id
        result["level"] = self._level
        return result

    def deserialize(self, data: Dict[str, Any]) -> None:
        self._id = data["id"]
        self._level = data["level"]

    @classmethod
    def createFromSerialized(cls, data: Dict[str, Any]) -> "Role":
        return Role(data["id"], data["level"])
