from typing import Optional
from models import UserInDB

class AuthMockDataService:
    def __init__(self):
        # In a real app, this would be a database. We store the hashed mock passwords here.
        # Test users can be aded using the register endpoint.
        self.users: dict[str, UserInDB] = {}
        self.next_id = 1

    def get_user_by_username(self, username: str) -> Optional[UserInDB]:
        if username in self.users:
            return self.users[username]
        return None

    def add_user(self, username: str, hashed_password: str) -> UserInDB:
        new_user = UserInDB(
            id=self.next_id,
            username=username,
            hashed_password=hashed_password
        )
        self.users[username] = new_user
        self.next_id += 1
        return new_user
