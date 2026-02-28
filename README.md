# DocSeal — Secure Academic Document Signing & Verification

[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![Status](https://img.shields.io/badge/Status-Stable-brightgreen.svg)](#)
[![Demo Mode](https://img.shields.io/badge/Demo%20Mode-Enabled-green.svg)](#demo-mode)

Comprehensive cryptographic solution for secure signing, encryption, and verification of academic documents. **Production-ready GUI** (PyQt6) with automated demo mode, full-featured CLI, and complete CA system.

**Key Highlights**: 🔐 RSA-2048 + AES-256-GCM | 📋 6 operation tabs with auto-load | 🚀 **Demo Mode automation** | 🏛️ Full CA with revocation | 🎨 Dark/Light themes | ⚡ Zero-config quick start

**Quick Links**: [Installation](#installation) | [GUI Guide](#gui-guide) | [Demo Mode](#demo-mode) | [CLI Commands](#cli-reference) | [Python API](#python-api) | [Security](#security)

---

## Features

✅ **Core Operations**:
- RSA-PSS-SHA256 signing with proof of authenticity
- AES-256-GCM encryption with integrity verification
- Two-layer operations: Sign+Encrypt and Decrypt+Verify
- Tamper detection with forensic evidence
- Certificate Authority system with revocation (CRL)
- Audit logging for compliance

✅ **GUI (PyQt6)**:
- **6 Operation Tabs**: Sign | Verify | Encrypt | Decrypt | Sign+Encrypt | Decrypt+Verify
- **Demo Mode**: One-click setup with automatic file/certificate population
- **CA Management**: Initialize CA, issue certificates, manage revocation, view audit logs
- **Themes**: Toggle between light and dark modes
- **Real-time Feedback**: Progress messages, success/error notifications
- **Intelligent File Loading**: Auto-detects file types (signed, encrypted, signed-encrypted)

✅ **CLI** (10+ commands):
- Full command-line interface with argparse
- Batch automation support
- CA management commands
- Verbose output and error handling

✅ **Python API**:
- `DocSealService` for programmatic access
- Full-featured cryptographic operations
- Certificate and key management

✅ **File Format**: 
- `.dseal` (ZIP-based) with JSON metadata, payload, signatures, certificates
- Tamper-proof with cryptographic verification

✅ **Security**:
- RSA-2048 asymmetric keys
- AES-256-GCM authenticated encryption
- PBKDF2 key derivation
- X.509 certificate validation
- CRL revocation checking
- Forensic audit trails

---

## Demo Mode

**What is Demo Mode?**

Demo Mode is a one-click setup feature that fully automates DocSeal for testing and demonstration. When enabled, the GUI automatically:
- ✅ Loads sample certificates and keys
- ✅ Populates all input/output fields
- ✅ Pre-selects correct file types for each operation
- ✅ Clears fields when disabled for clean state

**How to Use Demo Mode**:

1. Launch GUI: `docseal-gui`
2. Click **"Enable Demo Mode"** button (top toolbar or menu)
3. Navigate to any operation tab (Sign, Encrypt, etc.)
4. All fields auto-populate with demo data → Just click the operation button!
5. Output files automatically save to `data/` directory
6. Click **"Disable Demo Mode"** when finished

**Demo Mode Features**:
- Automatic file discovery by operation type
- Pre-populated certificates and keys from `data/certs/` and `data/keys/`
- One-click document processing (no manual selections)
- Real-time demo status indicator
- Field clearing on disable for fresh start

**Example Demo Workflow**:
```
GUI starts → Click "Enable Demo Mode" 
→ Go to "Sign+Encrypt" tab → Fields auto-populate
→ Click "Sign & Encrypt" → Output saved to data/
→ Go to "Decrypt+Verify" tab → Files auto-load
→ Click "Decrypt & Verify" → Success!
```

**Perfect for**: Demonstrations | Testing workflows | Training | Quick evaluation | CI/CD pipelines

**Requirements**: Python 3.11+ | OpenSSL dev headers | Linux/macOS/Windows

```bash
# Clone & setup
git clone <repo-url> && cd docseal
python3 -m venv .venv && source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r requirements.txt

# Optional: dev dependencies
pip install -r requirements-dev.txt

# Install package
pip install -e .

# Verify
docseal --help && docseal-gui
```

---

## Quick Start

### 🚀 GUI (Recommended — 30 seconds)

**Option 1: Demo Mode (Fastest — Zero Configuration)**
```bash
docseal-gui
# Click "Enable Demo Mode" button → Select any tab → Click operation → Done!
# All fields auto-populate with demo data, files auto-load
```

**Option 2: Manual Setup**
```bash
docseal-gui
# Navigate: **CA Tab** → Init CA → Issue Certificate → Use Sign/Verify/Encrypt/Decrypt tabs
```

### CLI (Quick Reference)

```bash
# Initialize CA (one-time setup)
docseal ca init                                              

# Issue certificate for a user
docseal ca issue --name "Alice" --role "Registrar" --valid-days 365

# Sign a document
docseal sign --input document.pdf --cert alice.p12 --output document.dseal

# Verify signature
docseal verify --envelope document.dseal --verbose

# Encrypt for secure sharing
docseal encrypt --input secret.pdf --cert recipient.pem --output secret.dseal

# Decrypt and verify (two-layer)
docseal decrypt --envelope secret.dseal --key recipient_key.pem
docseal decrypt-verify --envelope secure.dseal --key key.pem --signer-cert signer.pem

# Manage revocation
docseal ca list                                              # View revoked certs
docseal ca revoke --serial <number> --reason "compromised"  # Revoke cert
```

### Python API (Programmatic Use)

```python
from docseal.core.service import DocSealService
from docseal.core.envelope import DsealEnvelope
from cryptography import x509
from cryptography.hazmat.primitives import serialization

service = DocSealService()

# Load certificates and keys
with open('key.pem', 'rb') as f:
    key = serialization.load_pem_private_key(f.read(), password=None)
with open('cert.pem', 'rb') as f:
    cert = x509.load_pem_x509_certificate(f.read())

# Sign document
envelope = service.sign(b"document content", key, cert, description="Transcript")
with open('out.dseal', 'wb') as f:
    f.write(envelope.to_bytes())

# Verify signature
loaded = DsealEnvelope.from_bytes(open('out.dseal', 'rb').read())
result = service.verify(loaded, [cert])
if result.is_valid:
    print(f"✓ Valid signature from {result.signer_name}")
```

---

## GUI Guide

**How to Use the GUI**:

1. Launch with `docseal-gui`
2. Initialize CA: Go to **CA Tabs** → **Init CA** → Set password (8+ chars)
3. Issue certificates: **CA Tabs** → **Issue Cert** → Enter name/role → Create
4. Use operation tabs below for signing, encryption, etc.

**For Faster Demo**: Use **Demo Mode** (see [Demo Mode](#demo-mode) section) for automatic setup!

### Operation Tabs

| Tab | Purpose | Input | Process | Output |
|-----|---------|-------|---------|--------|
| **Sign** | Create signature | Document file + .p12 cert | Password → Sign | .signed.dseal |
| **Verify** | Authenticate | .dseal file (optional: signer cert) | Verify signature + CRL check | Signer name, timestamp, validity |
| **Encrypt** | Secure sharing | Document + recipient cert | Encrypt with recipient's public key | .encrypted.dseal |
| **Decrypt** | Unlock encrypted | .dseal file + your private cert | Password → Decrypt with your key | Plaintext document |
| **Sign+Encrypt** | Confidential & authenticated | Doc + signer cert + recipient cert | Sign then encrypt | .signed-encrypted.dseal |
| **Decrypt+Verify** | Auth + decrypt | .dseal file + your private cert + signer cert | Decrypt then verify signature | Document + verification result |

**Demo Mode Auto-Loading**:
- When **Demo Mode** is enabled, fields auto-populate with correct files
- Each tab intelligently loads appropriate file types:
  - **Verify Tab**: Loads `.signed.dseal` files
  - **Decrypt Tab**: Loads `*encrypted*.dseal` files (not signed-encrypted)
  - **Decrypt+Verify Tab**: Loads `*signed-encrypted*.dseal` files
  - **Sign+Encrypt Tab**: Loads certificates with matching keys for seamless encryption/decryption

### CA Management Tabs

| Tab | Purpose | Action |
|-----|---------|--------|
| **Init CA** | Initialize Certificate Authority | Set password (8+ chars) → Creates keypair & self-signed cert |
| **Issue Cert** | Issue new certificates | Enter name, role, validity days → Create signed certificate |
| **Revoke** | Revoke certificates | Select cert from dropdown → Choose reason → Confirm |
| **List** | View revoked certificates | Display revocation list with dates and reasons |
| **CA Info** | Authority information | Display CA certificate details and statistics |

### Themes
- **Toggle Light/Dark Mode**: Menu → Theme selection
- **Default**: Light theme with dark mode option

---

## CLI Reference

```bash
# Certificate Authority
docseal ca init                                    # Initialize new CA
docseal ca issue --name NAME --role ROLE --valid-days DAYS    # Issue cert
docseal ca revoke --serial SERIAL --reason REASON # Revoke cert
docseal ca list                                    # List revoked certs
docseal ca info                                    # CA information

# Document Operations  
docseal sign --input FILE --cert CERT.p12 [--output FILE.dseal]        # Sign
docseal verify --envelope FILE.dseal [--cert CERT.pem] [--verbose]     # Verify
docseal encrypt --input FILE --cert RECIPIENT.pem [--output FILE.dseal] # Encrypt
docseal decrypt --envelope FILE.dseal --key KEY.pem [--output FILE]    # Decrypt
docseal sign-encrypt --input FILE --signer-cert SIGNER.p12 --recipient-cert RECIPIENT.pem
docseal decrypt-verify --envelope FILE.dseal --key KEY.pem --signer-cert SIGNER.pem

# Options
--verbose                   # Detailed output
--no-revocation-check       # Skip CRL check (verify only)
--help, --version           # Show help/version
```

---

## Python API

**Service Methods**:
- `sign(document: bytes, key, cert, description: str) → DsealEnvelope`
- `verify(envelope: DsealEnvelope, trusted_certs: list) → VerificationResult`
- `encrypt(document: bytes, recipient_cert, description: str) → DsealEnvelope`
- `decrypt(envelope: DsealEnvelope, key) → bytes`
- `sign_encrypt(document, signer_key, signer_cert, recipient_cert, desc) → DsealEnvelope`
- `decrypt_and_verify(envelope, recipient_key, trusted_certs) → (bytes, VerificationResult)`

**Envelope**: Serialize with `envelope.to_bytes()` | Deserialize with `DsealEnvelope.from_bytes(data)`

**Full Example**:
```python
from docseal.core.service import DocSealService
from docseal.core.envelope import DsealEnvelope
from cryptography import x509
from cryptography.hazmat.primitives import serialization

service = DocSealService()

# Two-layer secure transfer
signer_key = serialization.load_pem_private_key(open('signer_key.pem', 'rb').read(), None)
signer_cert = x509.load_pem_x509_certificate(open('signer_cert.pem', 'rb').read())
recipient_cert = x509.load_pem_x509_certificate(open('recipient_cert.pem', 'rb').read())

envelope = service.sign_encrypt(open('sensitive.pdf', 'rb').read(), signer_key, signer_cert, recipient_cert)
with open('secure.dseal', 'wb') as f:
    f.write(envelope.to_bytes())

# Recipient side
recipient_key = serialization.load_pem_private_key(open('recipient_key.pem', 'rb').read(), None)
loaded = DsealEnvelope.from_bytes(open('secure.dseal', 'rb').read())
document, result = service.decrypt_and_verify(loaded, recipient_key, [signer_cert])

if result.is_valid:
    print(f"✓ Verified from {result.signer_name} at {result.signature_timestamp}")
    with open('decrypted.pdf', 'wb') as f:
        f.write(document)
```

---

## File Format (.dseal)

ZIP archive structure:
```
metadata.json          # {"version": "1.0", "payload_encrypted": false/true, "signer_name": "...", 
                       #  "signature_timestamp": "...", "algorithms": {...}, ...}
payload.bin            # Original document or AES-256-GCM ciphertext
signature.bin          # RSA-PSS-SHA256 signature (optional)
signer_cert.pem        # Signer's X.509 certificate (if signed)
recipient_cert.pem     # Recipient's certificate (if encrypted)
encrypted_key.bin      # RSA-OAEP wrapped AES key (if encrypted)
```

---

## Certificate Authority System

**Overview**: Full X.509 CA for issuing/revoking certificates with forensic audit logging.

**How It Works**: 
1. Init CA → RSA-2048 keypair + self-signed cert stored in `~/.docseal/ca/`
2. Issue certs → CA signs certificates with subject/issuer in separate X.509 extensions
3. Maintain CRL → Track revoked certs in `crl.json`
4. Verify against CRL → All signature verifications check revocation status

**Files** (in `~/.docseal/ca/`):
- `ca.pem` - CA certificate (PEM)
- `ca_key.pem` - CA private key (encrypted)
- `crl.json` - Certificate revocation list
- `audit.log` - Forensic audit trail

**Revocation Workflow**:
```bash
docseal ca revoke --serial 123456789 --reason "key-compromise"
# Updates crl.json with {serial, date_revoked, reason}
# Future verifications with that cert will fail
```

---

## Architecture

**Layer Model**:
```
┌─────────────────────────────────────┐
│  GUI (PyQt6)    │    CLI (argparse) │
│  6 op tabs      │    10+ commands   │
│  CA mgmt        │    Batch support  │
│  Dark/light     │                   │
└────────┬────────────────┬───────────┘
         │                │
    ┌────▼────────────────▼────┐
    │   Service Layer           │
    │  (DocSealService)         │
    │  sign, verify, encrypt,   │
    │  decrypt, sign_encrypt,   │
    │  decrypt_verify, CRL check│
    └────┬─────────────────────┘
         │
    ┌────▼──────────────────────┐
    │ Core Cryptographic Ops    │
    │ signing.py (RSA-PSS)      │
    │ verification.py (sig+CRL) │
    │ encryption.py (AES-GCM)   │
    │ decryption.py (AES-GCM)   │
    │ envelope.py (ZIP format)  │
    └────┬─────────────────────┘
         │
    ┌────▼──────────────────────┐
    │  cryptography lib (v42+)  │
    │  RSA, AES, X.509, PBKDF2  │
    └──────────────────────────┘
```

**Module Map** (src/docseal/):
```
core/              # Cryptographic operations
├── service.py        (DocSealService API)
├── envelope.py       (.dseal ZIP format)
├── signing.py        (RSA-PSS creation)
├── verification.py   (RSA verification + CRL)
├── encryption.py     (AES-256-GCM + RSA wrap)
└── decryption.py     (AES-256-GCM operations)

ca/                # Certificate Authority
├── authority.py      (CertificateAuthority)
├── certificates.py   (X.509 generation/validation)
├── revocation.py     (CRL management)
└── exceptions.py     (CA errors)

cli/               # Command-line interface
├── main.py          (Entry point, command routing)
├── sign.py, verify.py, encrypt.py, decrypt.py, ca.py
└── colors.py        (Color output)

gui/               # Graphical interface
├── app.py           (Entry point)
├── main_window.py   (Main window frame)
├── tabs.py          (Operation tabs: Sign, Verify, Encrypt, Decrypt, etc.)
├── ca_tabs.py       (CA tabs: Init, Issue, Revoke, List, Info)
├── ca_manager.py    (CA GUI controller)
├── service_wrapper.py (GUI service wrapper with file I/O)
├── themes.py        (Light/dark themes)
└── styles.py        (CSS styling)

audit/             # Audit logging
└── logger.py        (Forensic logging)

utils/             # Utilities
└── validation.py    (Input validation)
```

---

## Testing

```bash
# Run tests
pip install -r requirements-dev.txt
pytest tests/ -v                                    # All tests
pytest tests/test_integration_*.py -v              # Integration only
pytest tests/test_cli_*.py -v                      # CLI only
pytest tests/test_ca_*.py -v                       # CA only
pytest tests/ --cov=src/docseal --cov-report=html # With coverage

# Generate test certificates (RSA-2048, X.509)
python scripts/generate_test_keys.py
# Creates: registrar, lecturers, students, employer with keys/certs

# Test scenarios: signing, encryption, tamper detection, multi-signer, 
# revocation, certificate validation, CLI parsing, GUI interaction
```

---

## File Locations

**CA Storage** (`~/.docseal/ca/`): `ca.pem`, `ca_key.pem`, `crl.json`, `audit.log`

**Working Files**: Documents/certificates anywhere; `.dseal` output to input dir or `--output` location

**Config**: Linux/macOS: `~/.docseal/` | Windows: `%USERPROFILE%\.docseal\`

---

## Security

**Algorithms**:
| Operation | Algorithm | Standard |
|-----------|-----------|----------|
| Signing | RSA-PSS-SHA256 | PKCS#1 v2.1 |
| Encryption | AES-256-GCM | NIST |
| Key Wrapping | RSA-OAEP | PKCS#1 v2.1 |
| Key Derivation | PBKDF2-SHA256 | PKCS#5 |
| Asym Keys | RSA-2048 | NIST |

**Threat Model**:
- ✓ **Signature tampering**: Detected (RSA-PSS verification fails)
- ✓ **Encrypted payload tampering**: Detected (GCM auth fails)
- ✓ **Wrong key decryption**: Fails (GCM auth fails)
- ✓ **Revoked cert use**: Detected (CRL check)
- ✓ **Timestamp authenticity**: TSA integration for certified timestamps (v2.0)
- ✓ **Multi-recipient**: Full multi-recipient encryption support (v2.0)
- ✓ **HSM support**: Hardware Security Module integration (v2.0)

**Best Practices**: Strong passwords (8+ chars, mixed case/numbers/symbols) | Protect private keys | Verify external documents | Always enable CRL checks | Review audit logs | Backup CA | Renew certs before expiry | Keep software updated

**Assumptions**: Trusted environment for key storage | Secure cert distribution | No external timestamp authority (v0.9) | No HSM (v0.9)

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| CA not initialized | `docseal ca init` or GUI CA → Init CA |
| Document/file not found | Check path exists, use absolute paths, verify filename |
| Invalid certificate/password | Re-enter password (case-sensitive), re-issue if forgotten |
| Certificate revoked | `docseal ca list` to check, use different cert |
| SIGNATURE INVALID | Document modified after signing, wrong cert, expired cert, corrupted file |
| Permission denied | Check `~/.docseal/ca/` permissions with `ls -la`, fix if needed |
| Out of memory | Close other apps, increase RAM, split large documents |
| GUI won't start | `pip install -e '.[gui]'`, check X11/Wayland (Linux) |
| CLI commands not found | `pip install -e .` again, or use `python -m docseal.cli.main` |

---

## Recent Improvements (v1.0)

✅ **Demo Mode Automation**: One-click demo with automatic file/certificate population (v1.0)
✅ **Intelligent File Loading**: Type-specific auto-detection (.signed.dseal, .encrypted.dseal, .signed-encrypted.dseal)
✅ **Certificate Matching Fix**: Sign+Encrypt+Decrypt workflow now seamlessly preserves encryption keys
✅ **Thread Safety**: Eliminated segmentation faults in cryptographic operations
✅ **Error Recovery**: Graceful handling of deleted UI components
✅ **UI Polish**: Real-time progress messages, clean field population in demo mode

**Code Quality**:
```bash
mypy src/docseal --strict          # Type checking
ruff check src/                     # Linting
bandit -r src/docseal/             # Security audit
pytest tests/ --cov=src/docseal    # Coverage
```

**Contributing**: Fork → Feature branch → Add tests → Pass CI → PR

**Known v2.0 Limits**: Local-only CRL (no OCSP) | No WebUI yet

**v3.0 Roadmap**: OCSP integration | WebUI dashboard | Batch operations API | Blockchain notarization

---

## License

MIT - See [LICENSE](LICENSE)

**Support**: Open GitHub issues | Check existing issues | Review docs above

