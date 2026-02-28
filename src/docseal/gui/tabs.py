"""GUI tabs for DocSeal operations."""

from pathlib import Path
from typing import Optional

from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QCheckBox,
    QFileDialog,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from .ca_manager import CertificateAuthority
from .logger_widget import LoggerWidget, LogLevel
from .service_wrapper import GUIDocSealService


class WorkerThread(QThread):
    """Worker thread for long-running operations."""

    finished = pyqtSignal()
    error = pyqtSignal(str)
    success = pyqtSignal(str)
    progress = pyqtSignal(str)  # For progress updates

    def __init__(self, operation, *args, parent=None, **kwargs):
        super().__init__(parent)
        self.operation = operation
        self.args = args
        self.kwargs = kwargs
        self.setObjectName("WorkerThread")  # For debugging

    def run(self):
        """Run the operation."""
        try:
            self.progress.emit("Processing...")
            result = self.operation(*self.args, **self.kwargs)
            if result:
                self.success.emit(str(result))
            self.finished.emit()
        except Exception as e:
            self.error.emit(f"Error: {str(e)}")
            self.finished.emit()
        # No explicit quit/wait here; letting the thread exit naturally avoids
        # deadlock and "QThread: Destroyed while thread is still running" errors.


class SignTab(QWidget):
    """Tab for signing documents."""

    def __init__(self, ca_manager: Optional[CertificateAuthority] = None):
        super().__init__()
        self.service = GUIDocSealService()
        self.ca_manager = ca_manager
        self.demo_mode = False
        self.init_ui()
        self._check_demo_mode()
    
    def _check_demo_mode(self):
        """Check if demo mode is enabled and auto-load files."""
        try:
            from pathlib import Path
            import json
            
            # Only enable demo if .demo_config exists AND demo_mode is explicitly True
            config_file = Path("data") / ".demo_config"
            if config_file.exists():
                try:
                    config = json.loads(config_file.read_text())
                    # Only proceed if demo_mode is explicitly True (not just present)
                    if config.get("demo_mode") is True:
                        self.demo_mode = True
                        self._auto_load_demo_files()
                except Exception:
                    pass
        except Exception:
            pass
    
    def _auto_load_demo_files(self):
        """Auto-load demo files in demo mode."""
        try:
            from .demo_mode import DemoSetup
            demo = DemoSetup()
            result = demo.enable_demo_mode()
            
            # Auto-load sample document
            if result.get('sample_document'):
                self.document_path.setText(result['sample_document'])
            
            # Auto-load certificates if available
            certs_dir = Path('data/certs')
            keys_dir = Path('data/keys')
            
            if certs_dir.exists():
                certs = sorted(certs_dir.glob('*.pem'))
                if certs:
                    self.cert_path.setText(str(certs[0]))
            
            if keys_dir.exists():
                keys = sorted(keys_dir.glob('*.pem'))
                if keys:
                    self.key_path.setText(str(keys[0]))
            
            # Auto-generate output path
            if self.document_path.text():
                doc_path = Path(self.document_path.text())
                output = doc_path.parent / f"{doc_path.stem}.signed.dseal"
                self.output_path.setText(str(output))
        except Exception:
            pass
    
    def _clear_fields(self):
        """Clear all form fields when demo mode is disabled."""
        self.document_path.setText("")
        self.key_path.setText("")
        self.cert_path.setText("")
        self.output_path.setText("")
        self.description.clear()

    def init_ui(self):
        """Initialize the UI."""
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # Title
        title = QLabel("📄 Sign Document")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)

        # CA checkbox (shown always; disabled if CA missing)
        ca_group = QGroupBox("Certificate Authority")
        ca_layout = QVBoxLayout()
        self.use_ca_checkbox = QCheckBox("Use CA Certificate and Key")
        if not (self.ca_manager and self.ca_manager.ca_exists()):
            self.use_ca_checkbox.setEnabled(False)
            self.use_ca_checkbox.setToolTip("Initialize CA first in the CA tab")
        self.use_ca_checkbox.stateChanged.connect(self._toggle_ca_usage)
        ca_layout.addWidget(self.use_ca_checkbox)
        ca_group.setLayout(ca_layout)
        layout.addWidget(ca_group)

        # Document selection
        doc_group = self._create_file_selector("Document to Sign:", "document_path")
        layout.addWidget(doc_group)

        # Private key selection
        key_group = self._create_file_selector("Private Key:", "key_path")
        layout.addWidget(key_group)

        # Certificate selection
        cert_group = self._create_file_selector("Certificate:", "cert_path")
        layout.addWidget(cert_group)

        # Output file
        output_group = self._create_file_selector("Save As:", "output_path", save=True)
        layout.addWidget(output_group)

        # Description
        desc_label = QLabel("Description (optional):")
        layout.addWidget(desc_label)
        self.description = QTextEdit()
        self.description.setMaximumHeight(80)
        self.description.setPlaceholderText("Enter a description for this signature...")
        layout.addWidget(self.description)

        # Sign button
        sign_btn = QPushButton("Sign Document")
        sign_btn.setMinimumHeight(40)
        sign_btn.setStyleSheet("font-size: 11pt; font-weight: bold;")
        sign_btn.clicked.connect(self._sign)
        layout.addWidget(sign_btn)

        # Logger widget
        self.logger = LoggerWidget()
        layout.addWidget(self.logger)

        # Status (removed - now using logger)
        self.status = QLabel("Ready to sign documents")
        self.status.setStyleSheet("color: #7f8c8d; padding: 10px;")

        layout.addStretch()
        self.setLayout(layout)

    def _create_file_selector(
        self, label: str, attr: str, save: bool = False
    ) -> QGroupBox:
        """Create a file selector group."""
        group = QGroupBox(label)
        layout = QHBoxLayout()

        # Text field
        field = QLineEdit()
        field.setReadOnly(True)
        setattr(self, attr, field)
        layout.addWidget(field)

        # Browse button
        browse_btn = QPushButton("Browse...")
        if save:
            browse_btn.clicked.connect(lambda: self._browse_save(field))
        else:
            browse_btn.clicked.connect(lambda: self._browse_open(field))
        layout.addWidget(browse_btn)

        group.setLayout(layout)
        return group

    def _toggle_ca_usage(self):
        """Toggle CA usage and auto-populate fields."""
        if not self.use_ca_checkbox:
            return
        if self.use_ca_checkbox.isChecked():
            if self.ca_manager and self.ca_manager.ca_exists():
                self.key_path.setText(str(self.ca_manager.ca_key_path))
                self.cert_path.setText(str(self.ca_manager.ca_cert_path))
                self.key_path.setReadOnly(True)
                self.cert_path.setReadOnly(True)
            else:
                QMessageBox.warning(
                    self, "CA not available", "Initialize the CA in the CA tab first."
                )
                self.use_ca_checkbox.setChecked(False)
        else:
            self.key_path.setReadOnly(False)
            self.cert_path.setReadOnly(False)
            self.key_path.clear()
            self.cert_path.clear()

    def _browse_open(self, field: QLineEdit):
        """Open file browser for opening files."""
        path, _ = QFileDialog.getOpenFileName(self, "Select File")
        if path:
            field.setText(path)
            if (
                field is getattr(self, "envelope_path", None)
                and not self.output_path.text()
            ):
                default = Path(path).with_suffix(".decrypted")
                self.output_path.setText(str(default))
            if (
                field is getattr(self, "document_path", None)
                and not self.output_path.text()
            ):
                default = Path(path).with_suffix(".signed_encrypted.dseal")
                self.output_path.setText(str(default))
            if (
                field is getattr(self, "envelope_path", None)
                and not self.output_path.text()
            ):
                default = Path(path).with_suffix(".decrypted")
                self.output_path.setText(str(default))
            if (
                field is getattr(self, "document_path", None)
                and not self.output_path.text()
            ):
                default = Path(path).with_suffix(".encrypted.dseal")
                self.output_path.setText(str(default))
            if (
                field is getattr(self, "document_path", None)
                and not self.output_path.text()
            ):
                default = Path(path).with_suffix(".dseal")
                self.output_path.setText(str(default))

    def _browse_save(self, field: QLineEdit):
        """Open file browser for saving files."""
        path, _ = QFileDialog.getSaveFileName(
            self, "Save As", filter="DocSeal Envelopes (*.dseal)"
        )
        if path:
            if not path.endswith(".dseal"):
                path += ".dseal"
            field.setText(path)

    def _sign(self):
        """Sign the document."""
        doc_path = self.document_path.text()
        key_path = self.key_path.text()
        cert_path = self.cert_path.text()
        output_path = self.output_path.text()
        description = self.description.toPlainText()

        if not all([doc_path, key_path, cert_path, output_path]):
            QMessageBox.warning(
                self, "Missing Input", "Please select all required files."
            )
            self.logger.log_warning("Missing required file selections")
            return
        
        # Validate that all paths exist
        try:
            if not Path(doc_path).exists():
                raise FileNotFoundError(f"Document not found: {doc_path}")
            if not Path(key_path).exists():
                raise FileNotFoundError(f"Private key not found: {key_path}")
            if not Path(cert_path).exists():
                raise FileNotFoundError(f"Certificate not found: {cert_path}")
        except Exception as e:
            QMessageBox.warning(self, "File Not Found", str(e))
            self.logger.log_error(str(e))
            return

        self.logger.log_info(f"Starting signature on: {Path(doc_path).name}")
        self.logger.log_progress("Loading certificate...")
        self.logger.log_progress("Loading private key...")
        self.logger.log_progress("Computing signature...")
        self.logger.log_progress("Creating envelope...")

        def sign_op():
            # Don't call logger from worker thread - it causes GUI thread issues
            return self.service.sign(
                Path(doc_path),
                Path(key_path),
                Path(cert_path),
                Path(output_path),
                description,
            )

        thread = WorkerThread(sign_op, parent=self)
        thread.success.connect(
            lambda msg: self._on_sign_success(output_path)
        )
        thread.error.connect(self._on_sign_error)
        thread.finished.connect(thread.deleteLater)
        thread.start()

    def _on_sign_success(self, output_path: str):
        """Handle successful signing."""
        self.logger.log_success(f"✓ Document signed successfully!")
        self.logger.log_success(f"✓ Saved to: {output_path}")
        file_size = Path(output_path).stat().st_size if Path(output_path).exists() else 0
        self.logger.log_success(f"✓ File size: {file_size:,} bytes")
        QMessageBox.information(self, "Success", f"Document signed successfully!\n\nSaved to: {output_path}")
        # Reset form
        self.document_path.setText("")
        self.key_path.setText("")
        self.cert_path.setText("")
        self.output_path.setText("")
        self.description.clear()

    def _on_sign_error(self, error: str):
        """Handle signing error."""
        self.logger.log_error(error.replace("Error: ", ""))
        QMessageBox.critical(self, "Error", error)


class VerifyTab(QWidget):
    """Tab for verifying signatures."""

    def __init__(self):
        super().__init__()
        self.service = GUIDocSealService()
        self.demo_mode = False
        self.init_ui()
        self._check_demo_mode()
    
    def _check_demo_mode(self):
        """Check if demo mode is enabled and auto-load files."""
        try:
            from pathlib import Path
            import json
            
            # Only enable demo if .demo_config exists AND demo_mode is explicitly True
            config_file = Path("data") / ".demo_config"
            if config_file.exists():
                try:
                    config = json.loads(config_file.read_text())
                    # Only proceed if demo_mode is explicitly True (not just present)
                    if config.get("demo_mode") is True:
                        self.demo_mode = True
                        self._auto_load_demo_files()
                except Exception:
                    pass
        except Exception:
            pass
    
    def _auto_load_demo_files(self):
        """Auto-load demo signed file in demo mode."""
        try:
            # Look for .signed.dseal files (signed only, not signed-encrypted)
            docs_dir = Path('data/documents')
            if docs_dir.exists():
                signed_files = list(docs_dir.glob('*.signed.dseal'))
                if signed_files:
                    self.envelope_path.setText(str(signed_files[0]))
                else:
                    # Fall back to any .dseal file if no .signed.dseal exists
                    dseal_files = list(docs_dir.glob('*.dseal'))
                    if dseal_files:
                        self.envelope_path.setText(str(dseal_files[0]))
            
            # Auto-load certificate
            certs_dir = Path('data/certs')
            if certs_dir.exists():
                certs = sorted(certs_dir.glob('*.pem'))
                if certs:
                    # Store for later use in verify
                    self.trusted_cert = str(certs[0])
        except Exception:
            pass

    def init_ui(self):
        """Initialize the UI."""
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # Title
        title = QLabel("Verify Signature")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)

        # Envelope selection
        env_group = self._create_file_selector("Envelope File:", "envelope_path")
        layout.addWidget(env_group)

        # Certificate selection
        cert_group = self._create_file_selector("Signer Certificate:", "cert_path")
        layout.addWidget(cert_group)

        # Verify button
        verify_btn = QPushButton("Verify Signature")
        verify_btn.setMinimumHeight(40)
        verify_btn.setStyleSheet("font-size: 11pt; font-weight: bold;")
        verify_btn.clicked.connect(self._verify)
        layout.addWidget(verify_btn)

        # Logger widget
        self.logger = LoggerWidget()
        layout.addWidget(self.logger)

        # Results
        self.results = QTextEdit()
        self.results.setReadOnly(True)
        self.results.setMinimumHeight(150)
        layout.addWidget(QLabel("Detailed Results:"))
        layout.addWidget(self.results)

        # Status (deprecated - using logger instead)
        self.status = QLabel("Ready to verify signatures")
        self.status.setStyleSheet("color: #7f8c8d; padding: 10px;")

        layout.addStretch()
        self.setLayout(layout)

    def _create_file_selector(self, label: str, attr: str) -> QGroupBox:
        """Create a file selector group."""
        group = QGroupBox(label)
        layout = QHBoxLayout()

        field = QLineEdit()
        field.setReadOnly(True)
        setattr(self, attr, field)
        layout.addWidget(field)

        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(lambda: self._browse(field))
        layout.addWidget(browse_btn)

        group.setLayout(layout)
        return group

    def _browse(self, field: QLineEdit):
        """Open file browser."""
        path, _ = QFileDialog.getOpenFileName(self, "Select File")
        if path:
            field.setText(path)

    def _verify(self):
        """Verify the signature."""
        env_path = self.envelope_path.text()

        if not env_path:
            QMessageBox.warning(
                self, "Missing Input", "Please select the envelope to verify."
            )
            self.logger.log_warning("No envelope file selected")
            return
        
        # Validate that the path exists
        try:
            if not Path(env_path).exists():
                raise FileNotFoundError(f"Envelope file not found: {env_path}")
        except Exception as e:
            QMessageBox.warning(self, "File Not Found", str(e))
            self.logger.log_error(str(e))
            return

        self.logger.log_info(f"Verifying signature of: {Path(env_path).name}")
        self.logger.log_progress("Reading signed envelope...")
        self.logger.log_progress("Extracting signature...")
        self.logger.log_progress("Validating certificate chain...")
        self.logger.log_progress("Computing document hash...")
        self.logger.log_progress("Verifying signature...")
        self.results.clear()

        def verify_op():
            # Don't call logger from worker thread - causes GUI thread access violations
            result = self.service.verify(Path(env_path))
            return result

        thread = WorkerThread(verify_op, parent=self)
        thread.success.connect(self._display_results)
        thread.error.connect(self._on_verify_error)
        thread.finished.connect(thread.deleteLater)
        thread.start()

    def _display_results(self, result_str: str):
        """Display verification results."""
        try:
            self.results.setText(result_str)
            self.logger.log_success("✓ Signature verification completed!")
            self.logger.log_success("✓ Signature is VALID ✓ Document is AUTHENTIC")
        except Exception as e:
            self._on_verify_error(str(e))

    def _on_verify_error(self, error: str):
        """Handle error."""
        self.logger.log_error(error.replace("Error: ", ""))
        self.results.setText(error)
    
    def _clear_fields(self):
        """Clear all form fields when demo mode is disabled."""
        self.envelope_path.setText("")
        self.cert_path.setText("")
        self.trusted_cert = None
        self.results.setText("")


class EncryptTab(QWidget):
    """Tab for encrypting documents."""

    def __init__(self):
        super().__init__()
        self.service = GUIDocSealService()
        self.demo_mode = False
        self.init_ui()
        self._check_demo_mode()
    
    def _check_demo_mode(self):
        """Check if demo mode is enabled and auto-load files."""
        try:
            from pathlib import Path
            import json
            
            # Only enable demo if .demo_config exists AND demo_mode is explicitly True
            config_file = Path("data") / ".demo_config"
            if config_file.exists():
                try:
                    config = json.loads(config_file.read_text())
                    # Only proceed if demo_mode is explicitly True (not just present)
                    if config.get("demo_mode") is True:
                        self.demo_mode = True
                        self._auto_load_demo_files()
                except Exception:
                    pass
        except Exception:
            pass
    
    def _auto_load_demo_files(self):
        """Auto-load demo files in demo mode."""
        try:
            from .demo_mode import DemoSetup
            demo = DemoSetup()
            result = demo.enable_demo_mode()
            
            # Auto-load sample document
            if result.get('sample_document'):
                self.document_path.setText(result['sample_document'])
            
            # Auto-load recipient certificate
            certs_dir = Path('data/certs')
            if certs_dir.exists():
                certs = sorted(certs_dir.glob('*.pem'))
                if certs:
                    self.cert_path.setText(str(certs[0]))
            
            # Auto-generate output path
            if self.document_path.text():
                doc_path = Path(self.document_path.text())
                output = doc_path.parent / f"{doc_path.stem}.encrypted.dseal"
                self.output_path.setText(str(output))
        except Exception:
            pass

    def init_ui(self):
        """Initialize the UI."""
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # Title
        title = QLabel("Encrypt Document")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)

        # Document selection
        doc_group = self._create_file_selector("Document to Encrypt:", "document_path")
        layout.addWidget(doc_group)

        # Recipient certificate
        cert_group = self._create_file_selector("Recipient Certificate:", "cert_path")
        layout.addWidget(cert_group)

        # Output file
        output_group = self._create_file_selector("Save As:", "output_path", save=True)
        layout.addWidget(output_group)

        # Encrypt button
        encrypt_btn = QPushButton("Encrypt Document")
        encrypt_btn.setMinimumHeight(40)
        encrypt_btn.setStyleSheet("font-size: 11pt; font-weight: bold;")
        encrypt_btn.clicked.connect(self._encrypt)
        layout.addWidget(encrypt_btn)

        # Logger widget
        self.logger = LoggerWidget()
        layout.addWidget(self.logger)

        layout.addStretch()
        self.setLayout(layout)

    def _create_file_selector(
        self, label: str, attr: str, save: bool = False
    ) -> QGroupBox:
        """Create a file selector group."""
        group = QGroupBox(label)
        layout = QHBoxLayout()

        field = QLineEdit()
        field.setReadOnly(True)
        setattr(self, attr, field)
        layout.addWidget(field)

        browse_btn = QPushButton("Browse...")
        if save:
            browse_btn.clicked.connect(lambda: self._browse_save(field))
        else:
            browse_btn.clicked.connect(lambda: self._browse_open(field))
        layout.addWidget(browse_btn)

        group.setLayout(layout)
        return group

    def _browse_open(self, field: QLineEdit):
        """Open file browser for opening files."""
        path, _ = QFileDialog.getOpenFileName(self, "Select File")
        if path:
            field.setText(path)

    def _browse_save(self, field: QLineEdit):
        """Open file browser for saving files."""
        path, _ = QFileDialog.getSaveFileName(
            self, "Save As", filter="DocSeal Envelopes (*.dseal)"
        )
        if path:
            if not path.endswith(".dseal"):
                path += ".dseal"
            field.setText(path)

    def _encrypt(self):
        """Encrypt the document."""
        doc_path = self.document_path.text()
        cert_path = self.cert_path.text()
        output_path = self.output_path.text()

        if not all([doc_path, cert_path, output_path]):
            QMessageBox.warning(
                self, "Missing Input", "Please select all required files."
            )
            self.logger.log_warning("Missing required file selections")
            return
        
        # Validate that all paths exist
        try:
            if not Path(doc_path).exists():
                raise FileNotFoundError(f"Document not found: {doc_path}")
            if not Path(cert_path).exists():
                raise FileNotFoundError(f"Certificate not found: {cert_path}")
        except Exception as e:
            QMessageBox.warning(self, "File Not Found", str(e))
            self.logger.log_error(str(e))
            return

        self.logger.log_info(f"Starting encryption of: {Path(doc_path).name}")
        self.logger.log_progress("Reading document...")
        self.logger.log_progress("Encrypting with AES-256...")
        self.logger.log_progress("Creating envelope...")

        def encrypt_op():
            # Don't call logger from worker thread - causes GUI thread access violations
            return self.service.encrypt(
                Path(doc_path), Path(cert_path), Path(output_path)
            )

        thread = WorkerThread(encrypt_op, parent=self)
        thread.success.connect(
            lambda: self._on_encrypt_success(output_path)
        )
        thread.error.connect(self._on_encrypt_error)
        thread.finished.connect(thread.deleteLater)
        thread.start()

    def _on_encrypt_success(self, output_path: str):
        """Handle successful encryption."""
        self.logger.log_success("✓ Document encrypted successfully!")
        self.logger.log_success(f"✓ Saved to: {output_path}")
        file_size = Path(output_path).stat().st_size if Path(output_path).exists() else 0
        self.logger.log_success(f"✓ File size: {file_size:,} bytes")
        QMessageBox.information(self, "Success", f"Document encrypted successfully!\n\nSaved to: {output_path}")
        # Reset form
        self.document_path.setText("")
        self.cert_path.setText("")
        self.output_path.setText("")

    def _on_encrypt_error(self, error: str):
        """Handle encryption error."""
        self.logger.log_error(error.replace("Error: ", ""))
        QMessageBox.critical(self, "Error", error)
    
    def _clear_fields(self):
        """Clear all form fields when demo mode is disabled."""
        self.document_path.setText("")
        self.cert_path.setText("")
        self.output_path.setText("")


class DecryptTab(QWidget):
    """Tab for decrypting documents."""

    def __init__(self, ca_manager: Optional[CertificateAuthority] = None):
        super().__init__()
        self.service = GUIDocSealService()
        self.ca_manager = ca_manager
        self.use_ca_checkbox: Optional[QCheckBox] = None
        self.demo_mode = False
        self.init_ui()
        self._check_demo_mode()
    
    def _check_demo_mode(self):
        """Check if demo mode is enabled and auto-load files."""
        try:
            from pathlib import Path
            import json
            
            # Only enable demo if .demo_config exists AND demo_mode is explicitly True
            config_file = Path("data") / ".demo_config"
            if config_file.exists():
                try:
                    config = json.loads(config_file.read_text())
                    # Only proceed if demo_mode is explicitly True (not just present)
                    if config.get("demo_mode") is True:
                        self.demo_mode = True
                        self._auto_load_demo_files()
                except Exception:
                    pass
        except Exception:
            pass
    
    def _auto_load_demo_files(self):
        """Auto-load demo encrypted file in demo mode."""
        try:
            # Look for .encrypted.dseal files (encrypted only, not signed-encrypted)
            docs_dir = Path('data/documents')
            if docs_dir.exists():
                # Prioritize .encrypted.dseal over .signed-encrypted.dseal
                encrypted_files = list(docs_dir.glob('*encrypted*.dseal'))
                if encrypted_files:
                    # Sort to prefer .encrypted.dseal over .signed-encrypted.dseal
                    encrypted_files.sort(key=lambda p: (
                        'signed-encrypted' in str(p),  # signed-encrypted last
                        str(p)  # then alphabetically
                    ))
                    self.envelope_path.setText(str(encrypted_files[0]))
            
            # Auto-load private key
            keys_dir = Path('data/keys')
            if keys_dir.exists():
                keys = sorted(keys_dir.glob('*.pem'))
                if keys:
                    self.key_path.setText(str(keys[0]))
            
            # Auto-generate output path
            if self.envelope_path.text():
                env_path = Path(self.envelope_path.text())
                output = env_path.parent / f"{env_path.stem}.decrypted"
                self.output_path.setText(str(output))
        except Exception:
            pass

    def init_ui(self):
        """Initialize the UI."""
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # Title
        title = QLabel("Decrypt Document")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)

        # Envelope selection
        env_group = self._create_file_selector("Encrypted Envelope:", "envelope_path")
        layout.addWidget(env_group)

        # CA checkbox
        ca_group = QGroupBox("Key Source")
        ca_layout = QVBoxLayout()
        self.use_ca_checkbox = QCheckBox("Use CA Private Key")
        if not (self.ca_manager and self.ca_manager.ca_exists()):
            self.use_ca_checkbox.setEnabled(False)
            self.use_ca_checkbox.setToolTip("Initialize CA first in the CA tab")
        self.use_ca_checkbox.stateChanged.connect(self._toggle_ca_usage)
        ca_layout.addWidget(self.use_ca_checkbox)
        ca_group.setLayout(ca_layout)
        layout.addWidget(ca_group)

        # Private key selection
        key_group = self._create_file_selector("Private Key:", "key_path")
        layout.addWidget(key_group)

        # Output file
        output_group = self._create_file_selector("Save As:", "output_path", save=True)
        layout.addWidget(output_group)

        # Decrypt button
        decrypt_btn = QPushButton("Decrypt Document")
        decrypt_btn.setMinimumHeight(40)
        decrypt_btn.setStyleSheet("font-size: 11pt; font-weight: bold;")
        decrypt_btn.clicked.connect(self._decrypt)
        layout.addWidget(decrypt_btn)

        # Logger widget
        self.logger = LoggerWidget()
        layout.addWidget(self.logger)

        layout.addStretch()
        self.setLayout(layout)

    def _create_file_selector(
        self, label: str, attr: str, save: bool = False
    ) -> QGroupBox:
        """Create a file selector group."""
        group = QGroupBox(label)
        layout = QHBoxLayout()

        field = QLineEdit()
        field.setReadOnly(True)
        setattr(self, attr, field)
        layout.addWidget(field)

        browse_btn = QPushButton("Browse...")
        if save:
            browse_btn.clicked.connect(lambda: self._browse_save(field))
        else:
            browse_btn.clicked.connect(lambda: self._browse_open(field))
        layout.addWidget(browse_btn)

        group.setLayout(layout)
        return group

    def _browse_open(self, field: QLineEdit):
        """Open file browser for opening files."""
        path, _ = QFileDialog.getOpenFileName(self, "Select File")
        if path:
            field.setText(path)

    def _browse_save(self, field: QLineEdit):
        """Open file browser for saving files."""
        path, _ = QFileDialog.getSaveFileName(self, "Save As")
        if path:
            field.setText(path)

    def _decrypt(self):
        """Decrypt the document."""
        env_path = self.envelope_path.text()
        key_path = self.key_path.text()
        output_path = self.output_path.text()

        if not all([env_path, key_path, output_path]):
            QMessageBox.warning(
                self, "Missing Input", "Please select all required files."
            )
            self.logger.log_warning("Missing required file selections")
            return
        
        # Validate that all paths exist
        try:
            if not Path(env_path).exists():
                raise FileNotFoundError(f"Envelope file not found: {env_path}")
            if not Path(key_path).exists():
                raise FileNotFoundError(f"Private key not found: {key_path}")
        except Exception as e:
            QMessageBox.warning(self, "File Not Found", str(e))
            self.logger.log_error(str(e))
            return

        self.logger.log_info(f"Starting decryption of: {Path(env_path).name}")
        self.logger.log_progress(f"Loading private key: {Path(key_path).name}")
        self.logger.log_progress("Reading encrypted envelope...")
        self.logger.log_progress("Decrypting with AES-256...")
        self.logger.log_progress("Extracting document...")

        def decrypt_op():
            # Don't call logger from worker thread - causes GUI thread access violations
            return self.service.decrypt(
                Path(env_path), Path(key_path), Path(output_path)
            )

        thread = WorkerThread(decrypt_op, parent=self)
        thread.success.connect(
            lambda: self._on_decrypt_success(output_path)
        )
        thread.error.connect(self._on_decrypt_error)
        thread.finished.connect(thread.deleteLater)
        thread.start()

    def _toggle_ca_usage(self):
        """Auto-fill private key from CA if available."""
        if not self.use_ca_checkbox:
            return
        if self.use_ca_checkbox.isChecked():
            if self.ca_manager and self.ca_manager.ca_exists():
                self.key_path.setText(str(self.ca_manager.ca_key_path))
                self.key_path.setReadOnly(True)
            else:
                QMessageBox.warning(
                    self, "CA not available", "Initialize the CA in the CA tab first."
                )
                self.use_ca_checkbox.setChecked(False)
        else:
            self.key_path.setReadOnly(False)
            self.key_path.clear()

    def _on_decrypt_success(self, output_path: str):
        """Handle successful decryption."""
        self.logger.log_success("✓ Document decrypted successfully!")
        self.logger.log_success(f"✓ Saved to: {output_path}")
        file_size = Path(output_path).stat().st_size if Path(output_path).exists() else 0
        self.logger.log_success(f"✓ File size: {file_size:,} bytes")
        QMessageBox.information(self, "Success", f"Document decrypted successfully!\n\nSaved to: {output_path}")
        # Reset form
        self.envelope_path.setText("")
        self.key_path.setText("")
        self.output_path.setText("")

    def _on_decrypt_error(self, error: str):
        """Handle decryption error."""
        self.logger.log_error(error.replace("Error: ", ""))
        QMessageBox.critical(self, "Error", error)
    
    def _clear_fields(self):
        """Clear all form fields when demo mode is disabled."""
        self.envelope_path.setText("")
        self.key_path.setText("")
        self.output_path.setText("")


class SignEncryptTab(QWidget):
    """Tab for signing and encrypting documents (two-layer envelope)."""

    def __init__(self, ca_manager: Optional[CertificateAuthority] = None):
        super().__init__()
        self.service = GUIDocSealService()
        self.ca_manager = ca_manager
        self.use_ca_checkbox: Optional[QCheckBox] = None
        self.demo_mode = False
        self.init_ui()
        self._check_demo_mode()
    
    def _check_demo_mode(self):
        """Check if demo mode is enabled and auto-load files."""
        try:
            from pathlib import Path
            import json
            
            # Only enable demo if .demo_config exists AND demo_mode is explicitly True
            config_file = Path("data") / ".demo_config"
            if config_file.exists():
                try:
                    config = json.loads(config_file.read_text())
                    # Only proceed if demo_mode is explicitly True (not just present)
                    if config.get("demo_mode") is True:
                        self.demo_mode = True
                        self._auto_load_demo_files()
                except Exception:
                    pass
        except Exception:
            pass
    
    def _auto_load_demo_files(self):
        """Auto-load demo files in demo mode."""
        try:
            from .demo_mode import DemoSetup
            demo = DemoSetup()
            result = demo.enable_demo_mode()
            
            # Auto-load sample document
            if result.get('sample_document'):
                self.document_path.setText(result['sample_document'])
            
            # Auto-load signer certificate and key
            certs_dir = Path('data/certs')
            keys_dir = Path('data/keys')
            
            if certs_dir.exists():
                certs = sorted(certs_dir.glob('*.pem'))
                if certs:
                    self.cert_path.setText(str(certs[0]))
            
            if keys_dir.exists():
                keys = sorted(keys_dir.glob('*.pem'))
                if keys:
                    self.key_path.setText(str(keys[0]))
            
            # Auto-load recipient certificate
            # IMPORTANT: Use the SAME cert as signer to ensure decrypt matches encrypt
            # In demo mode, both signer and recipient use the same certificate
            if certs_dir.exists():
                certs = sorted(certs_dir.glob('*.pem'))
                if certs:
                    # Use first cert for BOTH signer and recipient
                    self.recipient_cert_path.setText(str(certs[0]))
            
            # Auto-generate output path
            if self.document_path.text():
                doc_path = Path(self.document_path.text())
                output = doc_path.parent / f"{doc_path.stem}.signed-encrypted.dseal"
                self.output_path.setText(str(output))
        except Exception:
            pass
    
    def _clear_fields(self):
        """Clear all form fields when demo mode is disabled."""
        self.document_path.setText("")
        self.key_path.setText("")
        self.cert_path.setText("")
        self.recipient_cert_path.setText("")
        self.output_path.setText("")
        self.description.clear()

    def init_ui(self):
        """Initialize the UI."""
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # Title
        title = QLabel("Sign & Encrypt Document")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)

        # Description
        desc = QLabel(
            "Sign a document with your key, then encrypt it for a recipient.\n"
            "This creates a two-layer envelope: signature + encryption."
        )
        desc.setStyleSheet("color: #7f8c8d; padding: 10px;")
        layout.addWidget(desc)

        # CA checkbox (shown always; disabled if CA missing)
        ca_group = QGroupBox("Certificate Authority")
        ca_layout = QVBoxLayout()
        self.use_ca_checkbox = QCheckBox("Use CA Certificate and Key for signing")
        if not (self.ca_manager and self.ca_manager.ca_exists()):
            self.use_ca_checkbox.setEnabled(False)
            self.use_ca_checkbox.setToolTip("Initialize CA first in the CA tab")
        self.use_ca_checkbox.stateChanged.connect(self._toggle_ca_usage)
        ca_layout.addWidget(self.use_ca_checkbox)
        ca_group.setLayout(ca_layout)
        layout.addWidget(ca_group)

        # Document selection
        doc_group = self._create_file_selector(
            "Document to Sign & Encrypt:", "document_path"
        )
        layout.addWidget(doc_group)

        # Signer key selection
        key_group = self._create_file_selector("Your Private Key:", "key_path")
        layout.addWidget(key_group)

        # Signer certificate selection
        signer_cert_group = self._create_file_selector("Your Certificate:", "cert_path")
        layout.addWidget(signer_cert_group)

        # Recipient certificate selection
        recipient_cert_group = self._create_file_selector(
            "Recipient's Certificate:", "recipient_cert_path"
        )
        layout.addWidget(recipient_cert_group)

        # Description field
        desc_group = QGroupBox("Signature Description (Optional):")
        desc_layout = QVBoxLayout()
        self.description = QTextEdit()
        self.description.setMinimumHeight(60)
        self.description.setPlaceholderText(
            "Enter signature description (e.g., 'Approved by Finance Team')"
        )
        desc_layout.addWidget(self.description)
        desc_group.setLayout(desc_layout)
        layout.addWidget(desc_group)

        # Output file
        output_group = self._create_file_selector("Save As:", "output_path", save=True)
        layout.addWidget(output_group)

        # Sign & Encrypt button
        sign_encrypt_btn = QPushButton("Sign & Encrypt Document")
        sign_encrypt_btn.setMinimumHeight(40)
        sign_encrypt_btn.setStyleSheet("font-size: 11pt; font-weight: bold;")
        sign_encrypt_btn.clicked.connect(self._sign_encrypt)
        layout.addWidget(sign_encrypt_btn)

        # Logger widget
        self.logger = LoggerWidget()
        layout.addWidget(self.logger)

        layout.addStretch()
        self.setLayout(layout)

    def _create_file_selector(
        self, label: str, attr: str, save: bool = False
    ) -> QGroupBox:
        """Create a file selector group."""
        group = QGroupBox(label)
        layout = QHBoxLayout()

        field = QLineEdit()
        field.setReadOnly(True)
        setattr(self, attr, field)
        layout.addWidget(field)

        browse_btn = QPushButton("Browse...")
        if save:
            browse_btn.clicked.connect(lambda: self._browse_save(field))
        else:
            browse_btn.clicked.connect(lambda: self._browse_open(field))
        layout.addWidget(browse_btn)

        group.setLayout(layout)
        return group

    def _browse_open(self, field: QLineEdit):
        """Open file browser for opening files."""
        path, _ = QFileDialog.getOpenFileName(self, "Select File")
        if path:
            field.setText(path)

    def _browse_save(self, field: QLineEdit):
        """Open file browser for saving files."""
        path, _ = QFileDialog.getSaveFileName(
            self, "Save As", filter="DocSeal Envelopes (*.dseal)"
        )
        if path:
            if not path.endswith(".dseal"):
                path += ".dseal"
            field.setText(path)

    def _sign_encrypt(self):
        """Sign and encrypt the document."""
        doc_path = self.document_path.text()
        key_path = self.key_path.text()
        cert_path = self.cert_path.text()
        recipient_cert_path = self.recipient_cert_path.text()
        output_path = self.output_path.text()
        description = self.description.toPlainText()

        if not all([doc_path, key_path, cert_path, recipient_cert_path, output_path]):
            QMessageBox.warning(
                self, "Missing Input", "Please select all required files."
            )
            self.logger.log_warning("Missing required file selections")
            return

        self.logger.log_info(f"Starting sign & encrypt of: {Path(doc_path).name}")
        self.logger.log_progress("Loading signer private key...")
        self.logger.log_progress("Computing signature...")
        self.logger.log_progress("Loading recipient certificate...")
        self.logger.log_progress("Encrypting with AES-256...")
        self.logger.log_progress("Creating signed+encrypted envelope...")

        def sign_encrypt_op():
            # Don't call logger from worker thread - causes GUI thread access violations
            return self.service.sign_encrypt(
                Path(doc_path),
                Path(key_path),
                Path(cert_path),
                Path(recipient_cert_path),
                Path(output_path),
                description,
            )

        thread = WorkerThread(sign_encrypt_op, parent=self)
        thread.success.connect(
            lambda: self._on_sign_encrypt_success(output_path)
        )
        thread.error.connect(self._on_sign_encrypt_error)
        thread.finished.connect(thread.deleteLater)
        thread.start()

    def _toggle_ca_usage(self):
        """Auto-fill signer key/cert from CA if available."""
        if not self.use_ca_checkbox:
            return
        if self.use_ca_checkbox.isChecked():
            if self.ca_manager and self.ca_manager.ca_exists():
                self.key_path.setText(str(self.ca_manager.ca_key_path))
                self.cert_path.setText(str(self.ca_manager.ca_cert_path))
                self.key_path.setReadOnly(True)
                self.cert_path.setReadOnly(True)
            else:
                QMessageBox.warning(
                    self, "CA not available", "Initialize the CA in the CA tab first."
                )
                self.use_ca_checkbox.setChecked(False)
        else:
            self.key_path.setReadOnly(False)
            self.cert_path.setReadOnly(False)
            self.key_path.clear()
            self.cert_path.clear()

    def _on_sign_encrypt_success(self, output_path: str):
        """Handle successful sign+encrypt."""
        self.logger.log_success("✓ Document signed AND encrypted successfully!")
        self.logger.log_success(f"✓ Saved to: {output_path}")
        file_size = Path(output_path).stat().st_size if Path(output_path).exists() else 0
        self.logger.log_success(f"✓ File size: {file_size:,} bytes")
        QMessageBox.information(self, "Success", f"Document signed and encrypted successfully!\n\nSaved to: {output_path}")
        # Reset form
        self.document_path.setText("")
        self.key_path.setText("")
        self.cert_path.setText("")
        self.recipient_cert_path.setText("")
        self.output_path.setText("")
        self.description.clear()

    def _on_sign_encrypt_error(self, error: str):
        """Handle sign+encrypt error."""
        self.logger.log_error(error.replace("Error: ", ""))
        QMessageBox.critical(self, "Error", error)
    
    def _clear_fields(self):
        """Clear all form fields when demo mode is disabled."""
        self.document_path.setText("")
        self.key_path.setText("")
        self.cert_path.setText("")
        self.recipient_cert_path.setText("")
        self.output_path.setText("")
        self.description.clear()


class DecryptVerifyTab(QWidget):
    """Tab for decrypting and verifying signed-encrypted documents."""

    def __init__(self, ca_manager: Optional[CertificateAuthority] = None):
        super().__init__()
        self.service = GUIDocSealService()
        self.ca_manager = ca_manager
        self.use_ca_checkbox: Optional[QCheckBox] = None
        self.demo_mode = False
        self.init_ui()
        self._check_demo_mode()
    
    def _check_demo_mode(self):
        """Check if demo mode is enabled and auto-load files."""
        try:
            from pathlib import Path
            import json
            
            # Only enable demo if .demo_config exists AND demo_mode is explicitly True
            config_file = Path("data") / ".demo_config"
            if config_file.exists():
                try:
                    config = json.loads(config_file.read_text())
                    # Only proceed if demo_mode is explicitly True (not just present)
                    if config.get("demo_mode") is True:
                        self.demo_mode = True
                        self._auto_load_demo_files()
                except Exception:
                    pass
        except Exception:
            pass
    
    def _auto_load_demo_files(self):
        """Auto-load demo signed-encrypted file in demo mode."""
        try:
            # Look for .signed-encrypted.dseal files specifically
            docs_dir = Path('data/documents')
            if docs_dir.exists():
                signed_encrypted_files = list(docs_dir.glob('*signed-encrypted*.dseal'))
                if signed_encrypted_files:
                    self.envelope_path.setText(str(signed_encrypted_files[0]))
                else:
                    # Fall back to any .dseal file if specific one doesn't exist
                    dseal_files = list(docs_dir.glob('*.dseal'))
                    if dseal_files:
                        self.envelope_path.setText(str(dseal_files[0]))
            
            # Auto-load private key
            keys_dir = Path('data/keys')
            if keys_dir.exists():
                keys = sorted(keys_dir.glob('*.pem'))
                if keys:
                    self.key_path.setText(str(keys[0]))
            
            # Auto-load trusted certificate (signer's cert)
            certs_dir = Path('data/certs')
            if certs_dir.exists():
                certs = sorted(certs_dir.glob('*.pem'))
                if certs:
                    self.trusted_cert_path.setText(str(certs[0]))
            
            # Auto-generate output path
            if self.envelope_path.text():
                env_path = Path(self.envelope_path.text())
                output = env_path.parent / f"{env_path.stem}.decrypted"
                self.output_path.setText(str(output))
        except Exception:
            pass

    def init_ui(self):
        """Initialize the UI."""
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # Title
        title = QLabel("Decrypt & Verify Document")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)

        # Description
        desc = QLabel(
            "Decrypt an encrypted document and verify its digital signature.\n"
            "Validates both the signer's identity and document integrity."
        )
        desc.setStyleSheet("color: #7f8c8d; padding: 10px;")
        layout.addWidget(desc)

        # Envelope selection
        env_group = self._create_file_selector("Encrypted Envelope:", "envelope_path")
        layout.addWidget(env_group)

        # CA checkbox
        ca_group = QGroupBox("Key Source")
        ca_layout = QVBoxLayout()
        self.use_ca_checkbox = QCheckBox("Use CA Private Key")
        if not (self.ca_manager and self.ca_manager.ca_exists()):
            self.use_ca_checkbox.setEnabled(False)
            self.use_ca_checkbox.setToolTip("Initialize CA first in the CA tab")
        self.use_ca_checkbox.stateChanged.connect(self._toggle_ca_usage)
        ca_layout.addWidget(self.use_ca_checkbox)
        ca_group.setLayout(ca_layout)
        layout.addWidget(ca_group)

        # Private key selection
        key_group = self._create_file_selector("Your Private Key:", "key_path")
        layout.addWidget(key_group)

        # Trusted certificates (for verification)
        trusted_group = self._create_file_selector(
            "Trusted CA Certificate (Optional):", "trusted_cert_path"
        )
        layout.addWidget(trusted_group)

        # Output file
        output_group = self._create_file_selector("Save As:", "output_path", save=True)
        layout.addWidget(output_group)

        # Decrypt & Verify button
        decrypt_verify_btn = QPushButton("Decrypt & Verify Document")
        decrypt_verify_btn.setMinimumHeight(40)
        decrypt_verify_btn.setStyleSheet("font-size: 11pt; font-weight: bold;")
        decrypt_verify_btn.clicked.connect(self._decrypt_verify)
        layout.addWidget(decrypt_verify_btn)

        # Logger widget
        self.logger = LoggerWidget()
        layout.addWidget(self.logger)

        # Verification result
        result_group = QGroupBox("Detailed Result:")
        result_layout = QVBoxLayout()
        self.result_display = QTextEdit()
        self.result_display.setReadOnly(True)
        self.result_display.setMinimumHeight(100)
        result_layout.addWidget(self.result_display)
        result_group.setLayout(result_layout)
        layout.addWidget(result_group)

        layout.addStretch()
        self.setLayout(layout)

    def _create_file_selector(
        self, label: str, attr: str, save: bool = False
    ) -> QGroupBox:
        """Create a file selector group."""
        group = QGroupBox(label)
        layout = QHBoxLayout()

        field = QLineEdit()
        field.setReadOnly(True)
        setattr(self, attr, field)
        layout.addWidget(field)

        browse_btn = QPushButton("Browse...")
        if save:
            browse_btn.clicked.connect(lambda: self._browse_save(field))
        else:
            browse_btn.clicked.connect(lambda: self._browse_open(field))
        layout.addWidget(browse_btn)

        group.setLayout(layout)
        return group

    def _browse_open(self, field: QLineEdit):
        """Open file browser for opening files."""
        path, _ = QFileDialog.getOpenFileName(self, "Select File")
        if path:
            field.setText(path)

    def _browse_save(self, field: QLineEdit):
        """Open file browser for saving files."""
        path, _ = QFileDialog.getSaveFileName(self, "Save As")
        if path:
            field.setText(path)

    def _decrypt_verify(self):
        """Decrypt and verify the document."""
        env_path = self.envelope_path.text()
        key_path = self.key_path.text()
        output_path = self.output_path.text()
        trusted_cert_path = self.trusted_cert_path.text()

        if not all([env_path, key_path, output_path]):
            QMessageBox.warning(
                self, "Missing Input", "Please select all required files."
            )
            self.logger.log_warning("Missing required file selections")
            return

        self.logger.log_info(f"Starting decrypt & verify of: {Path(env_path).name}")
        self.logger.log_progress(f"Loading private key: {Path(key_path).name}")
        self.logger.log_progress("Reading signed+encrypted envelope...")
        self.logger.log_progress("Decrypting with AES-256...")
        self.logger.log_progress("Extracting signature...")
        self.logger.log_progress("Validating certificate chain...")
        self.logger.log_progress("Verifying signature...")

        def decrypt_verify_op():
            # Don't call logger from worker thread - causes GUI thread access violations
            return self.service.decrypt_and_verify(
                Path(env_path),
                Path(key_path),
                Path(output_path),
                Path(trusted_cert_path) if trusted_cert_path else None,
            )

        thread = WorkerThread(decrypt_verify_op, parent=self)
        thread.success.connect(
            lambda: self._on_decrypt_verify_success(output_path)
        )
        thread.error.connect(self._on_decrypt_verify_error)
        thread.finished.connect(thread.deleteLater)
        thread.start()

    def _on_decrypt_verify_success(self, output_path: str):
        """Handle successful decrypt+verify."""
        self.logger.log_success("✓ Document decrypted successfully!")
        self.logger.log_success("✓ Signature verified successfully!")
        self.logger.log_success(f"✓ Saved to: {output_path}")
        file_size = Path(output_path).stat().st_size if Path(output_path).exists() else 0
        self.logger.log_success(f"✓ File size: {file_size:,} bytes")
        self.result_display.setText(
            "✓ Document DECRYPTED\n✓ Signature VALID\n✓ Document is AUTHENTIC and UNMODIFIED"
        )
        QMessageBox.information(self, "Success", f"Document decrypted and verified successfully!\n\nSaved to: {output_path}")
        # Reset form
        self.envelope_path.setText("")
        self.key_path.setText("")
        self.output_path.setText("")
        self.trusted_cert_path.setText("")

    def _on_decrypt_verify_error(self, error: str):
        """Handle decrypt+verify error."""
        self.logger.log_error(error.replace("Error: ", ""))
        self.result_display.setText(f"✗ FAILED\n{error.replace('Error: ', '')}")
        QMessageBox.critical(self, "Error", error)
    
    def _clear_fields(self):
        """Clear all form fields when demo mode is disabled."""
        self.envelope_path.setText("")
        self.key_path.setText("")
        self.trusted_cert_path.setText("")
        self.output_path.setText("")
        self.result_display.setText("")

    def _toggle_ca_usage(self):
        """Auto-fill private key from CA if available."""
        if not self.use_ca_checkbox:
            return
        if self.use_ca_checkbox.isChecked():
            if self.ca_manager and self.ca_manager.ca_exists():
                self.key_path.setText(str(self.ca_manager.ca_key_path))
                self.key_path.setReadOnly(True)
            else:
                QMessageBox.warning(
                    self, "CA not available", "Initialize the CA in the CA tab first."
                )
                self.use_ca_checkbox.setChecked(False)
        else:
            self.key_path.setReadOnly(False)
            self.key_path.clear()
