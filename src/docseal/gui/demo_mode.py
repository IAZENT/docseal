"""Demo mode for quick video presentation setup."""

import json
from pathlib import Path
from datetime import datetime


class DemoSetup:
    """Sets up demo data for quick video presentation."""

    def __init__(self, data_dir: Path = Path("data")) -> None:
        """Initialize demo setup."""
        self.data_dir = data_dir
        self.certs_dir = data_dir / "certs"
        self.keys_dir = data_dir / "keys"
        self.docs_dir = data_dir / "documents"

    def create_demo_structure(self) -> None:
        """Create demo directory structure."""
        self.certs_dir.mkdir(parents=True, exist_ok=True)
        self.keys_dir.mkdir(parents=True, exist_ok=True)
        self.docs_dir.mkdir(parents=True, exist_ok=True)

        # Create demo config
        config = {
            "demo_mode": True,
            "created_at": datetime.now().isoformat(),
            "quick_workflows": True,
            "auto_load": True,
        }
        
        config_file = self.data_dir / ".demo_config"
        config_file.write_text(json.dumps(config, indent=2))

    def create_sample_document(self) -> Path:
        """Create a sample document for signing."""
        sample_doc = self.docs_dir / "sample_document.txt"
        sample_doc.write_text(
            """ACADEMIC TRANSCRIPT
        
Institution: Demo University
Student: John Doe
Student ID: 20241001
Date: 2024-01-15

Courses Completed:
- Cryptography (A)
- Network Security (A-)
- Database Systems (A)
- Software Engineering (B+)

GPA: 3.85
Status: Good Standing

This is a sample document for demonstration purposes.
"""
        )
        return sample_doc

    def create_demo_certificates(self) -> tuple:
        """Check for existing demo certificates or return None."""
        try:
            # Check if certificates already exist
            cert_path = self.certs_dir / "demo_cert.pem"
            key_path = self.keys_dir / "demo_key.pem"
            
            if cert_path.exists() and key_path.exists():
                return str(cert_path), str(key_path)
            
            # If not, return None - user can use existing certs
            return None, None
        except Exception as e:
            print(f"Note: Demo certificates not available: {e}")
            return None, None

    def is_demo_mode(self) -> bool:
        """Check if demo mode is enabled."""
        config_file = self.data_dir / ".demo_config"
        if config_file.exists():
            try:
                config = json.loads(config_file.read_text())
                return config.get("demo_mode", False)
            except Exception:
                return False
        return False

    def enable_demo_mode(self) -> dict:
        """Enable demo mode with all setup. Returns paths to auto-load files."""
        self.create_demo_structure()
        sample_doc = self.create_sample_document()
        cert_path, key_path = self.create_demo_certificates()
        
        return {
            "sample_document": str(sample_doc) if sample_doc else None,
            "certificate": cert_path,
            "key": key_path,
            "demo_enabled": True,
        }

    def disable_demo_mode(self) -> None:
        """Disable demo mode."""
        config_file = self.data_dir / ".demo_config"
        if config_file.exists():
            config_file.unlink()  # Remove the config file completely


class QuickWorkflow:
    """Quick workflow helpers for demo."""

    @staticmethod
    def get_quick_sign_workflow() -> dict:
        """Get quick sign workflow steps."""
        return {
            "title": "Quick Sign Document",
            "steps": [
                "1. Click 'Select Document' - uses sample_document.txt",
                "2. Click 'Auto-Load Certificate' - loads default cert",
                "3. Click 'Auto-Load Key' - loads default key",
                "4. Click 'Sign' - Done!",
            ],
            "estimated_time": "< 30 seconds",
        }

    @staticmethod
    def get_quick_verify_workflow() -> dict:
        """Get quick verify workflow steps."""
        return {
            "title": "Quick Verify Signature",
            "steps": [
                "1. Click 'Select Envelope' - uses signed.dseal",
                "2. Click 'Auto-Load Certificate' - loads signer's cert",
                "3. Click 'Verify' - Done!",
            ],
            "estimated_time": "< 20 seconds",
        }

    @staticmethod
    def get_quick_encrypt_decrypt_workflow() -> dict:
        """Get quick encrypt/decrypt workflow steps."""
        return {
            "title": "Quick Encrypt & Decrypt",
            "steps": [
                "Encrypt: Select doc → Auto-load cert → Encrypt",
                "Decrypt: Select envelope → Auto-load key → Decrypt",
            ],
            "estimated_time": "< 40 seconds",
        }

    @staticmethod
    def get_ca_workflow() -> dict:
        """Get CA workflow steps."""
        return {
            "title": "Certificate Authority Setup",
            "steps": [
                "1. Go to CA Tab → Initialize CA",
                "2. Set password (e.g., 'demo123pass')",
                "3. Issue Certificate for user",
                "4. Use certificate for signing",
            ],
            "estimated_time": "~ 1 minute",
        }


class QuickStart:
    """Quick start guide for new users."""

    @staticmethod
    def get_quick_start_guide() -> str:
        """Get quick start guide text."""
        return """
╔════════════════════════════════════════════════════════════════╗
║           DOCSEAL QUICK START GUIDE                           ║
╚════════════════════════════════════════════════════════════════╝

🚀 GETTING STARTED (< 2 minutes)

1️⃣  LOGIN
   - Username: admin
   - Password: admin123
   
2️⃣  CREATE CA (First Time Only)
   - Click "CA Management"
   - Click "Initialize CA"
   - Set a password
   
3️⃣  ISSUE CERTIFICATE
   - Click "Issue Certificate"
   - Fill in name and role
   - Certificate is auto-generated
   
4️⃣  SIGN DOCUMENT
   - Click "Sign Document"
   - Select your document
   - Click "Sign" - it auto-loads everything!
   
5️⃣  VERIFY SIGNATURE
   - Click "Verify Signature"
   - Select the signed file (.dseal)
   - Click "Verify" - Done!

📊 DEMO WORKFLOWS (Watch the magic!)

✓ Sign & Verify: Shows cryptographic integrity
✓ Encrypt & Decrypt: Shows confidentiality
✓ Multi-layer: Sign then encrypt for full protection
✓ Audit Trail: See what was signed, when, by whom

🔐 KEY FEATURES

• RSA-2048 encryption
• AES-256-GCM for confidentiality  
• SHA-256 digital signatures
• Full certificate authority system
• Tamper detection
• Audit logging
• Multi-user support
• Role-based access control

💡 TIPS FOR VIDEO

• Use "Demo Mode" for quick workflows
• Pre-load sample documents
• Highlight the verification results
• Show timestamp and signer info
• Demonstrate CA dashboard
• Show audit logs
• Use light theme for better visibility

❓ HELP & SUPPORT

• Hover over buttons for tooltips
• Check dashboard for system status
• All operations are reversible
• Check logs for detailed info
"""

    @staticmethod
    def get_demo_script() -> str:
        """Get a demo script for presentation."""
        return """
╔════════════════════════════════════════════════════════════════╗
║           DOCSEAL DEMO SCRIPT (5 MINUTES)                     ║
╚════════════════════════════════════════════════════════════════╝

[INTRO - 30 seconds]
"Welcome to DocSeal, a secure document signing and verification 
system. Today I'll demonstrate how it makes cryptographic 
operations simple and secure."

[LOGIN - 20 seconds]
1. Show login screen
2. Login with admin/admin123
3. Highlight dashboard with user info and system status

[CERTIFICATE AUTHORITY - 60 seconds]
1. Click "CA Management"
2. Show "Initialize CA" - explain what CA does
3. Click "Issue Certificate"
4. Issue a certificate for a user
5. Show issued certificates list

[SIGN DOCUMENT - 60 seconds]
1. Go to "Sign Document" tab
2. Select a document (auto-suggested)
3. Click "Auto-Load Certificate" 
4. Click "Auto-Load Key"
5. Click "Sign"
6. Show the generated .dseal file

[VERIFY SIGNATURE - 60 seconds]
1. Go to "Verify Signature" tab
2. Select the .dseal file
3. Click "Auto-Load Certificate"
4. Click "Verify"
5. Show verification result with signer info and timestamp

[ADVANCED - 60 seconds]
1. Show "Encrypt & Decrypt" for confidentiality
2. Show "Sign + Encrypt" for combined protection
3. Explain multi-layer security
4. Show audit log

[CLOSING - 30 seconds]
"DocSeal makes cryptography accessible for everyone.
Secure, simple, powerful. That's DocSeal."

TOTAL TIME: ~5 minutes
"""
