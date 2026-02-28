"""Persistent logging widget for operation feedback."""

from datetime import datetime
from enum import Enum
from typing import Optional

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QTextCursor
from PyQt6.QtWidgets import QTextEdit, QWidget, QVBoxLayout, QLabel


class LogLevel(Enum):
    """Log levels."""

    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"


class LoggerWidget(QWidget):
    """Widget for displaying persistent operation logs."""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """Initialize the logger widget."""
        super().__init__(parent)
        self.init_ui()

    def init_ui(self) -> None:
        """Initialize UI."""
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)

        # Title
        title = QLabel("📋 Operation Log")
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(10)
        title.setFont(title_font)
        layout.addWidget(title)

        # Log display
        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        self.log_display.setMinimumHeight(150)
        self.log_display.setMaximumHeight(200)
        self.log_display.setStyleSheet(
            """
            QTextEdit {
                background-color: #2c3e50;
                color: #ecf0f1;
                border: 1px solid #34495e;
                border-radius: 4px;
                padding: 8px;
                font-family: monospace;
                font-size: 9pt;
            }
            """
        )
        layout.addWidget(self.log_display)

        self.setLayout(layout)

    def log(self, message: str, level: LogLevel = LogLevel.INFO) -> None:
        """Add a log message."""
        timestamp = datetime.now().strftime("%H:%M:%S")

        # Color coding
        color_map = {
            LogLevel.INFO: "#3498db",  # Blue
            LogLevel.SUCCESS: "#27ae60",  # Green
            LogLevel.WARNING: "#f39c12",  # Orange
            LogLevel.ERROR: "#e74c3c",  # Red
        }

        # Level indicator
        level_map = {
            LogLevel.INFO: "ℹ️ ",
            LogLevel.SUCCESS: "✅ ",
            LogLevel.WARNING: "⚠️ ",
            LogLevel.ERROR: "❌ ",
        }

        color = color_map[level]
        level_indicator = level_map[level]

        # Format the message
        html_message = (
            f'<span style="color: #95a5a6;">[{timestamp}]</span> '
            f'<span style="color: {color};">{level_indicator}{message}</span>'
        )

        # Append to log
        cursor = self.log_display.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.log_display.setTextCursor(cursor)
        self.log_display.insertHtml(html_message + "<br>")

        # Auto-scroll to bottom
        cursor = self.log_display.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.log_display.setTextCursor(cursor)

    def log_info(self, message: str) -> None:
        """Log info message."""
        self.log(message, LogLevel.INFO)

    def log_success(self, message: str) -> None:
        """Log success message."""
        self.log(message, LogLevel.SUCCESS)

    def log_warning(self, message: str) -> None:
        """Log warning message."""
        self.log(message, LogLevel.WARNING)

    def log_error(self, message: str) -> None:
        """Log error message."""
        self.log(message, LogLevel.ERROR)

    def log_progress(self, message: str) -> None:
        """Log progress message (same as info but for operations)."""
        self.log(f"⏳ {message}", LogLevel.INFO)

    def clear(self) -> None:
        """Clear all logs."""
        self.log_display.clear()
