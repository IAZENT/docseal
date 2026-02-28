"""Enhanced error handling and user-friendly messages."""

import traceback
from typing import Optional, Callable
from enum import Enum
from PyQt6.QtWidgets import QMessageBox
from PyQt6.QtCore import QObject, pyqtSignal


class ErrorLevel(Enum):
    """Error severity levels."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class ErrorHandler:
    """Handles errors with user-friendly messages."""

    # Error message mappings
    FRIENDLY_MESSAGES = {
        "FileNotFoundError": "The file could not be found. Please check the path and try again.",
        "ValueError": "Invalid input. Please check your values and try again.",
        "KeyError": "Required data is missing. Please ensure all fields are filled.",
        "PermissionError": "You don't have permission to access this file or folder.",
        "InvalidSignature": "Signature verification failed. Document may be tampered.",
        "IOError": "Error reading or writing file. Check disk space and permissions.",
        "OSError": "System error. Please try again or restart the application.",
        "RuntimeError": "An unexpected error occurred. Please check your inputs.",
        "TypeError": "Invalid data type provided. Please check your inputs.",
        "Exception": "An unexpected error occurred. Please contact support if this persists.",
    }

    @staticmethod
    def get_friendly_message(exception: Exception) -> str:
        """Get user-friendly error message."""
        exc_type = type(exception).__name__
        
        # Try exact match first
        if exc_type in ErrorHandler.FRIENDLY_MESSAGES:
            return ErrorHandler.FRIENDLY_MESSAGES[exc_type]
        
        # Try to find partial match
        for error_type, message in ErrorHandler.FRIENDLY_MESSAGES.items():
            if error_type.lower() in exc_type.lower():
                return message
        
        # Return generic message with original error
        original_msg = str(exception)
        if original_msg:
            return f"{ErrorHandler.FRIENDLY_MESSAGES['Exception']}\n\nDetails: {original_msg}"
        return ErrorHandler.FRIENDLY_MESSAGES["Exception"]

    @staticmethod
    def handle_exception(
        exception: Exception,
        title: str = "Error",
        level: ErrorLevel = ErrorLevel.ERROR,
        parent=None,
        callback: Optional[Callable] = None,
    ) -> None:
        """
        Handle exception with user-friendly dialog.

        Args:
            exception: The exception to handle
            title: Dialog title
            level: Error severity level
            parent: Parent widget
            callback: Optional callback after user acknowledges
        """
        friendly_msg = ErrorHandler.get_friendly_message(exception)
        details = traceback.format_exc()

        if level == ErrorLevel.CRITICAL:
            QMessageBox.critical(parent, title, friendly_msg)
        elif level == ErrorLevel.ERROR:
            QMessageBox.warning(parent, title, friendly_msg)
        elif level == ErrorLevel.WARNING:
            QMessageBox.warning(parent, title, friendly_msg)
        else:
            QMessageBox.information(parent, title, friendly_msg)

        if callback:
            callback()

    @staticmethod
    def log_exception(exception: Exception, context: str = "") -> None:
        """Log exception for debugging."""
        import logging
        
        logger = logging.getLogger("docseal")
        if context:
            logger.error(f"[{context}] {type(exception).__name__}: {str(exception)}")
        else:
            logger.error(f"{type(exception).__name__}: {str(exception)}")
        logger.debug(traceback.format_exc())


class OperationResult:
    """Result of an operation."""

    def __init__(
        self,
        success: bool,
        message: str,
        data: Optional[dict] = None,
        error: Optional[Exception] = None,
    ):
        """Initialize result."""
        self.success = success
        self.message = message
        self.data = data or {}
        self.error = error

    def __bool__(self) -> bool:
        """Check if operation was successful."""
        return self.success

    def __repr__(self) -> str:
        """String representation."""
        status = "✓" if self.success else "✗"
        return f"OperationResult({status} {self.message})"


class SafeOperation:
    """Context manager for safe operations."""

    def __init__(
        self,
        operation_name: str,
        parent=None,
        show_errors: bool = True,
    ):
        """Initialize safe operation."""
        self.operation_name = operation_name
        self.parent = parent
        self.show_errors = show_errors
        self.exception: Optional[Exception] = None

    def __enter__(self):
        """Enter context."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context and handle exceptions."""
        if exc_type is None:
            return True

        self.exception = exc_val
        
        if self.show_errors and exc_val:
            ErrorHandler.handle_exception(
                exc_val,
                title=f"{self.operation_name} Failed",
                parent=self.parent,
            )

        # Log the exception
        ErrorHandler.log_exception(exc_val, context=self.operation_name)

        return False

    def is_success(self) -> bool:
        """Check if operation was successful."""
        return self.exception is None


class ValidationError(Exception):
    """Custom validation error."""

    pass


class ValidatorHelper:
    """Helper for input validation."""

    @staticmethod
    def validate_file_path(path: str, must_exist: bool = True) -> tuple[bool, str]:
        """Validate file path."""
        from pathlib import Path
        
        if not path or not path.strip():
            return False, "Path cannot be empty"

        try:
            p = Path(path)
            if must_exist and not p.exists():
                return False, f"File not found: {path}"
            if p.exists() and not p.is_file():
                return False, f"Not a file: {path}"
            return True, ""
        except Exception as e:
            return False, f"Invalid path: {str(e)}"

    @staticmethod
    def validate_password(password: str, min_length: int = 8) -> tuple[bool, str]:
        """Validate password."""
        if not password:
            return False, "Password cannot be empty"
        if len(password) < min_length:
            return False, f"Password must be at least {min_length} characters"
        return True, ""

    @staticmethod
    def validate_email(email: str) -> tuple[bool, str]:
        """Validate email address."""
        import re
        
        if not email or not email.strip():
            return False, "Email cannot be empty"
        
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(pattern, email):
            return False, "Invalid email format"
        
        return True, ""

    @staticmethod
    def validate_username(username: str, min_length: int = 3) -> tuple[bool, str]:
        """Validate username."""
        if not username or not username.strip():
            return False, "Username cannot be empty"
        if len(username) < min_length:
            return False, f"Username must be at least {min_length} characters"
        if not username.replace("_", "").replace("-", "").isalnum():
            return False, "Username can only contain letters, numbers, - and _"
        return True, ""
