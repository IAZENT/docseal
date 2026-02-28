"""Authentication and session management for DocSeal GUI."""

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional

from .user_database import PersistentUserDatabase


@dataclass
class User:
    """Represents an authenticated user."""

    username: str
    role: str  # admin, operator, auditor
    email: str
    organization: str
    logged_in_at: datetime


class AuthenticationManager:
    """Manages user authentication and sessions."""

    def __init__(self, db_path: Optional[Path] = None):
        """
        Initialize the authentication manager.

        Args:
            db_path: Path to user database file
        """
        self.current_user: Optional[User] = None
        self.db = PersistentUserDatabase(db_path)

    def login(self, username: str, password: str) -> tuple[bool, str]:
        """
        Authenticate a user.

        Args:
            username: Username
            password: Password

        Returns:
            Tuple of (success, message)
        """
        if not self.db.user_exists(username):
            return False, "User not found"

        if not self.db.verify_password(username, password):
            return False, "Invalid password"

        # Get user info from database
        user_info = self.db.get_user(username)
        if not user_info:
            return False, "Failed to retrieve user information"

        # Update last login
        self.db.update_last_login(username)

        # Create user session
        self.current_user = User(
            username=username,
            role=user_info["role"],
            email=user_info["email"],
            organization=user_info["organization"],
            logged_in_at=datetime.now(),
        )

        return True, f"Welcome {username}!"

    def logout(self) -> None:
        """Log out the current user."""
        self.current_user = None

    def is_authenticated(self) -> bool:
        """Check if a user is authenticated."""
        return self.current_user is not None

    def get_current_user(self) -> Optional[User]:
        """Get the current authenticated user."""
        return self.current_user

    def create_user(
        self, username: str, password: str, role: str, email: str, organization: str
    ) -> tuple[bool, str]:
        """
        Create a new user (admin only).

        Args:
            username: Username
            password: Password
            role: User role (admin, operator, auditor)
            email: Email address
            organization: Organization name

        Returns:
            Tuple of (success, message)
        """
        if not self.current_user or self.current_user.role != "admin":
            return False, "Only administrators can create users"

        return self.db.create_user(username, password, role, email, organization)

    def _hash_password(self, password: str) -> str:
        """Hash a password."""
        import bcrypt
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt(rounds=12)).decode()

    def _verify_password(self, password: str, password_hash: str) -> bool:
        """Verify a password against its hash."""
        import bcrypt
        try:
            return bcrypt.checkpw(password.encode(), password_hash.encode())
        except Exception:
            return False

    def can_perform_action(self, action: str) -> bool:
        """Check if current user can perform an action."""
        if not self.current_user:
            return False

        role = self.current_user.role

        # Action-based permissions
        permissions = {
            "admin": [
                "login",
                "logout",
                "sign",
                "verify",
                "encrypt",
                "decrypt",
                "issue_cert",
                "revoke_cert",
                "init_ca",
                "manage_users",
            ],
            "operator": [
                "login",
                "logout",
                "sign",
                "verify",
                "encrypt",
                "decrypt",
                "issue_cert",
            ],
            "auditor": ["login", "logout", "verify", "view_logs"],
        }

        return action in permissions.get(role, [])
