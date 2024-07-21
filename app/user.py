import hashlib
from datetime import datetime

from storage.db_manager import create_user, get_user_by_username, update_user, delete_user, update_last_login


class User:
    def __init__(self, user_id, username, password, created_at, last_login=None):
        self.user_id = user_id
        self.username = username
        self.password = password
        self.created_at = created_at
        self.last_login = datetime.now() if last_login else None

    @staticmethod
    def create(username, password, created_at):
        hashed_password = User._hash_password(password)
        user_id = create_user(username, hashed_password, created_at)
        print(f"User created: {username}")
        return User(user_id, username, hashed_password, created_at)

    @staticmethod
    def get_by_username(username):
        user_data = get_user_by_username(username)
        if user_data:
            print(f"User retrieved: {username}")
            return User(*user_data)
        print(f"User not found: {username}")
        return None

    def update(self, username=None, password=None):
        if username:
            self.username = username
        if password:
            self.password = User._hash_password(password)
        update_user(self.user_id, username, self.password)
        print(f"User updated: {self.username}")

    def delete(self):
        delete_user(self.user_id)
        print(f"User deleted: {self.username}")

    def update_last_login(self):
        update_last_login(self.username)
        self.last_login = datetime.now()
        print(f"Last login updated for user: {self.username}")

    @staticmethod
    def _hash_password(password):
        """Hash a password using SHA-256."""
        return hashlib.sha256(password.encode('utf-8')).hexdigest()

    def check_password(self, password):
        """Check if the provided password matches the stored password."""
        return self.password == self._hash_password(password)

    def reset_password(self, new_password):
        self.password = self._hash_password(new_password)
        update_user(self.user_id, self.username, self.password)
        print(f"Password updated successfully for user: {self.username}")
