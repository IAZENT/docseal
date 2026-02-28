"""Quick start and help dialogs."""

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QDialog,
    QLabel,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from .demo_mode import QuickStart, QuickWorkflow, DemoSetup


class QuickStartDialog(QDialog):
    """Quick start guide dialog."""

    def __init__(self, parent: QWidget | None = None) -> None:
        """Initialize the dialog."""
        super().__init__(parent)
        self.setWindowTitle("DocSeal Quick Start Guide")
        self.setGeometry(100, 100, 700, 600)
        self.init_ui()

    def init_ui(self) -> None:
        """Initialize UI."""
        layout = QVBoxLayout()

        # Title
        title = QLabel("Quick Start Guide")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)

        # Guide text
        guide_text = QTextEdit()
        guide_text.setReadOnly(True)
        guide_text.setText(QuickStart.get_quick_start_guide())
        guide_text.setStyleSheet("font-family: monospace; font-size: 10pt;")
        layout.addWidget(guide_text)

        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)

        self.setLayout(layout)


class DemoScriptDialog(QDialog):
    """Demo script dialog for presentations."""

    def __init__(self, parent: QWidget | None = None) -> None:
        """Initialize the dialog."""
        super().__init__(parent)
        self.setWindowTitle("DocSeal Demo Script (5 minutes)")
        self.setGeometry(100, 100, 800, 650)
        self.init_ui()

    def init_ui(self) -> None:
        """Initialize UI."""
        layout = QVBoxLayout()

        # Title
        title = QLabel("Demo Script - 5 Minute Presentation")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)

        # Script text
        script_text = QTextEdit()
        script_text.setReadOnly(True)
        script_text.setText(QuickStart.get_demo_script())
        script_text.setStyleSheet("font-family: monospace; font-size: 9pt;")
        layout.addWidget(script_text)

        # Buttons
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)

        self.setLayout(layout)


class WorkflowHelpDialog(QDialog):
    """Workflow help dialog."""

    def __init__(self, workflow_type: str = "sign", parent: QWidget | None = None) -> None:
        """Initialize the dialog."""
        super().__init__(parent)
        self.workflow_type = workflow_type
        self.setWindowTitle(f"Quick {workflow_type.title()} Workflow")
        self.setGeometry(200, 200, 500, 400)
        self.init_ui()

    def init_ui(self) -> None:
        """Initialize UI."""
        layout = QVBoxLayout()

        # Get workflow info
        if self.workflow_type == "sign":
            workflow = QuickWorkflow.get_quick_sign_workflow()
        elif self.workflow_type == "verify":
            workflow = QuickWorkflow.get_quick_verify_workflow()
        elif self.workflow_type == "encrypt":
            workflow = QuickWorkflow.get_quick_encrypt_decrypt_workflow()
        elif self.workflow_type == "ca":
            workflow = QuickWorkflow.get_ca_workflow()
        else:
            workflow = QuickWorkflow.get_quick_sign_workflow()

        # Title
        title = QLabel(workflow["title"])
        title_font = QFont()
        title_font.setPointSize(12)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)

        # Steps
        steps_text = "\n".join(workflow["steps"])
        steps_label = QLabel(steps_text)
        steps_label.setWordWrap(True)
        steps_label.setStyleSheet("padding: 10px; font-size: 11pt; line-height: 1.6;")
        layout.addWidget(steps_label)

        # Time estimate
        time_label = QLabel(f"⏱️ Estimated Time: {workflow['estimated_time']}")
        time_label.setStyleSheet("font-weight: bold; padding: 10px; color: #3B82F6;")
        layout.addWidget(time_label)

        # Close button
        close_btn = QPushButton("Got it!")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)

        self.setLayout(layout)


class DemoModeSetupDialog(QDialog):
    """Dialog to enable demo mode."""

    def __init__(self, parent: QWidget | None = None) -> None:
        """Initialize the dialog."""
        super().__init__(parent)
        self.setWindowTitle("Enable Demo Mode")
        self.setGeometry(300, 300, 500, 350)
        self.init_ui()

    def init_ui(self) -> None:
        """Initialize UI."""
        layout = QVBoxLayout()

        # Title
        title = QLabel("✨ Enable Demo Mode")
        title_font = QFont()
        title_font.setPointSize(12)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)

        # Description
        desc = QLabel(
            "Demo Mode sets up:\n"
            "• Sample documents for quick testing\n"
            "• Auto-load certificates and keys\n"
            "• Quick workflow hints\n"
            "• Pre-configured demo data\n\n"
            "Perfect for video demonstrations!"
        )
        desc.setStyleSheet("padding: 10px; font-size: 10pt; line-height: 1.5;")
        desc.setWordWrap(True)
        layout.addWidget(desc)

        # Buttons
        btn_layout = QVBoxLayout()
        enable_btn = QPushButton("✓ Enable Demo Mode")
        enable_btn.clicked.connect(self._enable_demo)
        enable_btn.setStyleSheet(
            "background-color: #10B981; color: white; padding: 10px; font-weight: bold;"
        )
        btn_layout.addWidget(enable_btn)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        layout.addLayout(btn_layout)
        self.setLayout(layout)

    def _enable_demo(self) -> None:
        """Enable demo mode."""
        from pathlib import Path
        
        demo = DemoSetup(Path("data"))
        demo.enable_demo_mode()
        self.accept()
