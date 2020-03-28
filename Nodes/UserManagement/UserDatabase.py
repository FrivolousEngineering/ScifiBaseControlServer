from typing import Dict, Optional, Any, Iterator

from Nodes.UserManagement.User import User


class UserDatabase:
    def __init__(self) -> None:
        self._users = {}  # type: Dict[str, User]


        # DEBUG CODE!
        self.addUser(User("Admin", "The", "Overlord"))

    def addUser(self, user: User) -> None:
        self._users[user.id] = user

    def getUser(self, identifier: str) -> Optional[User]:
        return self._users.get(identifier)

    def getAllUsers(self) -> Iterator[User]:
        for user in self._users.values():
            yield user

    def serialize(self) -> Dict[str, Any]:
        data = dict()  # type: Dict[str, Any]
        data["users"] = []
        for user in self.getAllUsers():
            data["users"].append(user.serialize())
        return data

    def deserialize(self, data: Dict[str, Any]) -> None:
        self._users = {}

        for user in data["users"]:
            self._users[user["id"]] = User.createFromSerialized(user)
