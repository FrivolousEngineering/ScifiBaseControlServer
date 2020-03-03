from typing import Dict, Optional

from Nodes.UserManagement.User import User


class UserDatabase:
    def __init__(self) -> None:
        self._users = {}  # type: Dict[str, User]

    def addUser(self, user: User) -> None:
        self._users[user.id] = user

    def getUser(self, identifier: str) -> Optional[User]:
        return self._users.get(identifier)

    def getAllUsers(self):
        yield self._users.values()
