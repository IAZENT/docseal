"""Persistent user database management for DocSeal."""

import json
from pathlib import Path
from typing import Optional
import bcrypt
from datetime import datetime


class PersistentUserDatabase:
    """Manages persistent storage of user accounts with proper password hashing."""

    def __init__(self, db_path: Optional[Path] = None) -> None:
        """
        Initialize the user database.

        Args:
            db_path: Path to store users database JSON file
        """
        if db_path is None:
            db_path = Path.home() / ".docseal" / "users.json"
        
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._ensure_db_exists()

    def _ensure_db_exists(self) -> None:
        """Ensure database file exists with initial admin user."""
        if not self.db_path.exists():
            # Create initial admin user (password: admin123)
            admin_hash = bcrypt.hashpw(b"admin123", bcrypt.gensalt(rounds=12)).decode()
            initial_db = {
                "admin": {
                    "password_hash": admin_hash,
                    "role": "admin",
                    "email": "admin@docseal.local",
                    "organization": "DocSeal System",
                    "created_at": datetime.now().isoformat(),
                    "last_login": None,
                }
            }
            self._save_db(initial_db)

    def _load_db(self) -> dict:
        """Load user database from file."""
        try:
            return json.loads(self.db_path.read_text())
        except Exception:
            return {}

    def _save_db(self, data: dict) -> None:
        """Save user database to file."""
        self.db_path.write_text(json.dumps(data, indent=2))

    def user_exists(self, username: str) -> bool:
        """Check if user exists."""
        db = self._load_db()
        return username in db

    def get_user(self, username: str) -> Optional[dict]:
        """Get user data by username."""
        db = self._load_db()
        return db.get(username)

    def verify_password(self, username: str, password: str) -> bool:
        """Verify user password."""
        user = self.get_user(username)
        if not user:
            return False
        
        try:
            return bcrypt.checkpw(password.encode(), user["password_hash"].encode())
        except Exception:
            return False

    def create_user(
        self,
        username: str,
        password: str,
        role: str,
        email: str,
        organization: str,
    ) -> tuple[bool, str]:
        """
        Create a new user.

        Args:
            username: Username
            password: Password
            role: User role (admin, operator, auditor)
            email: Email address
            organization: Organization name

        Returns:
            Tuple of (success, message)
        """
        if not username or len(username) < 3:
            return False, "Username must be at least 3 characters"
        
        if not password or len(password) < 8:
            return False, "Password must be at least 8 characters"
        
        if role not in ["admin", "operator", "auditor"]:
            return False, "Invalid role"
        
        if self.user_exists(username):
            return False, "User already exists"
        
        try:
            db = self._load_db()
            password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt(rounds=12)).decode()
            
            db[username] = {
                "password_hash": password_hash,
                "role": role,
                "email": email,
                "organization": organization,
                "created_at": datetime.now().isoformat(),
                "last_login": None,
            }
            
            self._save_db(db)
            return True, f"User '{username}' created successfully"
        except Exception as e:
            return False, f"Failed to create user: {str(e)}"

    def update_user(
        self,
        username: str,
        **kwargs
    ) -> tuple[bool, str]:
        """Update user information."""
        user = self.get_user(username)
        if not user:
            return False, "User not found"
        
        db = self._load_db()
        
        # Allow updating: role, email, organization
        for key in ["role", "email", "organization"]:
            if key in kwargs:
                user[key] = kwargs[key]
        
        db[username] = user
        self._save_db(db)
        return True, "User updated successfully"

    def delete_user(self, username: str) -> tuple[bool, str]:
        """Delete a user."""
        if username == "admin":
            return False, "Cannot delete admin user"
        
        db = self._load_db()
        if username not in db:
            return False, "User not found"
        
        del db[username]
        self._save_db(db)
        return True, "User deleted successfully"

    def update_last_login(self, username: str) -> None:
        """Update last login timestamp for user."""
        user = self.get_user(username)
        if user:
            db = self._load_db()
            user["last_login"] = datetime.now().isoformat()
            db[username] = user
            self._save_db(db)

    def list_users(self) -> list[dict]:
        """Get list of all users (sanitized)."""
        db = self._load_db()
        users = []
        for username, user_data in db.items():
            users.append({
                "username": username,
                "role": user_data.get("role"),
                "email": user_data.get("email"),
                "organization": user_data.get("organization"),
                "created_at": user_data.get("created_at"),
                "last_login": user_data.get("last_login"),
            })
        return users

    def change_password(self, username: str, old_password: str, new_password: str) -> tuple[bool, str]:
        """Change user password."""
        if not self.verify_password(username, old_password):
            return False, "Current password is incorrect"
        
        if len(new_password) < 8:
            return False, "New password must be at least 8 characters"
        
        try:
            db = self._load_db()
            user = db[username]
            password_hash = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt(rounds=12)).decode()
            user["password_hash"] = password_hash
            db[username] = user
            self._save_db(db)
            return True, "Password changed successfully"
        except Exception as e:
            return False, f"Failed to change password: {str(e)}"
