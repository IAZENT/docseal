"""Admin panel for user management."""

from pathlib import Path
from typing import Optional

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QIcon
from PyQt6.QtWidgets import (
    QComboBox,
    QDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from .auth import AuthenticationManager
from .user_database import PersistentUserDatabase


class UserManagementDialog(QDialog):
    """Dialog for creating/editing users."""

    def __init__(self, parent: Optional[QWidget] = None, db: Optional[PersistentUserDatabase] = None, edit_user: Optional[str] = None) -> None:
        """Initialize the dialog."""
        super().__init__(parent)
        self.db = db
        self.edit_user = edit_user
        self.init_ui()
        self.setModal(True)
        self.setWindowTitle("Add User" if not edit_user else f"Edit User: {edit_user}")

    def init_ui(self) -> None:
        """Initialize UI."""
        layout = QVBoxLayout()
        layout.setSpacing(10)

        # Username
        username_label = QLabel("Username:")
        layout.addWidget(username_label)
        self.username_input = QLineEdit()
        self.username_input.setMinimumWidth(300)
        if self.edit_user:
            self.username_input.setText(self.edit_user)
            self.username_input.setReadOnly(True)
        layout.addWidget(self.username_input)

        # Password (if creating)
        if not self.edit_user:
            password_label = QLabel("Password (min 8 characters):")
            layout.addWidget(password_label)
            self.password_input = QLineEdit()
            self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
            layout.addWidget(self.password_input)

        # Role
        role_label = QLabel("Role:")
        layout.addWidget(role_label)
        self.role_combo = QComboBox()
        self.role_combo.addItems(["operator", "auditor", "admin"])
        layout.addWidget(self.role_combo)

        # Email
        email_label = QLabel("Email:")
        layout.addWidget(email_label)
        self.email_input = QLineEdit()
        layout.addWidget(self.email_input)

        # Organization
        org_label = QLabel("Organization:")
        layout.addWidget(org_label)
        self.org_input = QLineEdit()
        layout.addWidget(self.org_input)

        # Load existing data if editing
        if self.edit_user and self.db:
            user_info = self.db.get_user(self.edit_user)
            if user_info:
                self.role_combo.setCurrentText(user_info.get("role", "operator"))
                self.email_input.setText(user_info.get("email", ""))
                self.org_input.setText(user_info.get("organization", ""))

        # Buttons
        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self._save)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

        self.setLayout(layout)

    def _save(self) -> None:
        """Save user."""
        username = self.username_input.text().strip()
        role = self.role_combo.currentText()
        email = self.email_input.text().strip()
        organization = self.org_input.text().strip()

        if not username or not email or not organization:
            QMessageBox.warning(self, "Error", "Please fill all fields")
            return

        if self.edit_user:
            # Update existing user
            if self.db:
                success, msg = self.db.update_user(self.edit_user, role=role, email=email, organization=organization)
                if success:
                    QMessageBox.information(self, "Success", msg)
                    self.accept()
                else:
                    QMessageBox.warning(self, "Error", msg)
        else:
            # Create new user
            password = self.password_input.text()
            if not password or len(password) < 8:
                QMessageBox.warning(self, "Error", "Password must be at least 8 characters")
                return
            if self.db:
                success, msg = self.db.create_user(username, password, role, email, organization)
                if success:
                    QMessageBox.information(self, "Success", msg)
                    self.accept()
                else:
                    QMessageBox.warning(self, "Error", msg)

    def get_data(self) -> dict:
        """Get dialog data."""
        return {
            "username": self.username_input.text(),
            "role": self.role_combo.currentText(),
            "email": self.email_input.text(),
            "organization": self.org_input.text(),
        }


class AdminPanel(QWidget):
    """Admin panel for user management."""

    user_updated = pyqtSignal()

    def __init__(self, auth_manager: AuthenticationManager) -> None:
        """Initialize admin panel."""
        super().__init__()
        self.auth_manager = auth_manager
        self.db = auth_manager.db
        self.init_ui()

    def init_ui(self) -> None:
        """Initialize UI."""
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # Title
        title = QLabel("👥 User Management")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)

        # User table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Username", "Role", "Email", "Organization", "Last Login"])
        self.table.setColumnWidth(0, 120)
        self.table.setColumnWidth(1, 100)
        self.table.setColumnWidth(2, 150)
        self.table.setColumnWidth(3, 150)
        self.table.setColumnWidth(4, 150)
        layout.addWidget(self.table)

        # Buttons layout
        btn_layout = QHBoxLayout()

        add_btn = QPushButton("➕ Add User")
        add_btn.clicked.connect(self._add_user)
        btn_layout.addWidget(add_btn)

        edit_btn = QPushButton("✎ Edit User")
        edit_btn.clicked.connect(self._edit_user)
        btn_layout.addWidget(edit_btn)

        delete_btn = QPushButton("🗑️ Delete User")
        delete_btn.clicked.connect(self._delete_user)
        btn_layout.addWidget(delete_btn)

        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.clicked.connect(self._load_users)
        btn_layout.addWidget(refresh_btn)

        layout.addLayout(btn_layout)

        self.setLayout(layout)
        self._load_users()

    def _load_users(self) -> None:
        """Load and display users."""
        users = self.db.list_users()
        self.table.setRowCount(len(users))

        for row, user in enumerate(users):
            self.table.setItem(row, 0, QTableWidgetItem(user["username"]))
            self.table.setItem(row, 1, QTableWidgetItem(user["role"]))
            self.table.setItem(row, 2, QTableWidgetItem(user["email"]))
            self.table.setItem(row, 3, QTableWidgetItem(user["organization"]))
            last_login = user.get("last_login", "Never")
            if last_login:
                last_login = last_login.split("T")[0]  # Show date only
            self.table.setItem(row, 4, QTableWidgetItem(last_login))

    def _add_user(self) -> None:
        """Add new user."""
        dialog = UserManagementDialog(self, self.db)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self._load_users()
            self.user_updated.emit()

    def _edit_user(self) -> None:
        """Edit selected user."""
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Error", "Please select a user to edit")
            return

        username = self.table.item(current_row, 0).text()
        if username == "admin" and self.auth_manager.current_user and self.auth_manager.current_user.username != "admin":
            QMessageBox.warning(self, "Error", "Cannot edit admin user")
            return

        dialog = UserManagementDialog(self, self.db, username)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self._load_users()
            self.user_updated.emit()

    def _delete_user(self) -> None:
        """Delete selected user."""
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Error", "Please select a user to delete")
            return

        username = self.table.item(current_row, 0).text()
        if username == "admin":
            QMessageBox.warning(self, "Error", "Cannot delete admin user")
            return

        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to delete user '{username}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            success, msg = self.db.delete_user(username)
            if success:
                QMessageBox.information(self, "Success", msg)
                self._load_users()
                self.user_updated.emit()
            else:
                QMessageBox.warning(self, "Error", msg)
