from typing import List, Dict, Any

from Nodes.UserManagement.Role import Role


class User:
    def __init__(self, identifier: str = "", first_name: str = "", last_name: str = "") -> None:
        self._id = identifier

        self._first_name = first_name
        self._last_name = last_name

        self._roles = []  # type: List[Role]

    @property
    def id(self) -> str:  # pylint: disable=C0103
        return self._id

    @property
    def first_name(self) -> str:
        return self._first_name

    @property
    def last_name(self) -> str:
        return self._last_name

    @property
    def full_name(self) -> str:
        return self.first_name + " " + self.last_name

    def serialize(self) -> Dict[str, Any]:
        result = dict()  # type: Dict[str, Any]
        result["roles"] = []
        for role in self._roles:
            result["roles"].append(role.serialize())
        result["first_name"] = self._first_name
        result["last_name"] = self._last_name
        result["id"] = self._id
        return result

    def deserialize(self, data: Dict[str, Any]) -> None:
        for role in data["roles"]:
            self._roles.append(Role.createFromSerialized(role))

        self._first_name = data["first_name"]
        self._last_name = data["last_name"]
        self._id = data["id"]

    @classmethod
    def createFromSerialized(cls, data: Dict[str, Any]) -> "User":
        user = User()
        user.deserialize(data)
        return user
