"""Smart certificate auto-loader for simplified workflows."""

from pathlib import Path
from typing import Optional, Tuple
from cryptography import x509
from cryptography.hazmat.primitives import serialization


class CertificateCache:
    """Caches loaded certificates and keys in memory for quick access."""

    def __init__(self) -> None:
        """Initialize the cache."""
        self._cert_cache: dict[str, x509.Certificate] = {}
        self._key_cache: dict[str, object] = {}

    def get_certificate(self, path: Path) -> Optional[x509.Certificate]:
        """Get cached certificate or load from file."""
        path_str = str(path.absolute())
        if path_str in self._cert_cache:
            return self._cert_cache[path_str]
        
        try:
            cert_pem = path.read_bytes()
            cert = x509.load_pem_x509_certificate(cert_pem)
            self._cert_cache[path_str] = cert
            return cert
        except Exception:
            return None

    def get_key(self, path: Path, password: Optional[bytes] = None) -> Optional[object]:
        """Get cached key or load from file."""
        path_str = str(path.absolute())
        cache_key = path_str + (password.hex() if password else "none")
        
        if cache_key in self._key_cache:
            return self._key_cache[cache_key]
        
        try:
            key_pem = path.read_bytes()
            key = serialization.load_pem_private_key(key_pem, password=password)
            self._key_cache[cache_key] = key
            return key
        except Exception:
            return None

    def clear(self) -> None:
        """Clear all caches."""
        self._cert_cache.clear()
        self._key_cache.clear()


class SmartCertificateLoader:
    """Intelligently discovers and loads certificates and keys."""

    def __init__(self, search_paths: Optional[list[Path]] = None) -> None:
        """
        Initialize the loader.

        Args:
            search_paths: Paths to search for certificates
        """
        if search_paths is None:
            search_paths = [
                Path("data/certs"),
                Path.home() / ".docseal" / "certs",
                Path.cwd() / "certs",
            ]
        
        self.search_paths = [p for p in search_paths if p.exists()]
        self.cache = CertificateCache()

    def find_certificates(self) -> list[Tuple[str, Path]]:
        """
        Find all available certificates.

        Returns:
            List of (name, path) tuples
        """
        certs = []
        for search_path in self.search_paths:
            if search_path.exists():
                for cert_file in search_path.glob("*.pem"):
                    try:
                        # Verify it's actually a certificate
                        self.cache.get_certificate(cert_file)
                        certs.append((cert_file.stem, cert_file))
                    except Exception:
                        pass
        
        return sorted(certs, key=lambda x: x[0])

    def find_keys(self) -> list[Tuple[str, Path]]:
        """Find all available keys."""
        keys = []
        for search_path in self.search_paths:
            if search_path.exists():
                for key_file in search_path.glob("*key*.pem"):
                    if "pub" not in key_file.name:  # Skip public keys
                        keys.append((key_file.stem, key_file))
        
        return sorted(keys, key=lambda x: x[0])

    def get_certificate_by_name(self, name: str) -> Optional[x509.Certificate]:
        """Get certificate by name."""
        for cert_name, cert_path in self.find_certificates():
            if cert_name.lower() == name.lower():
                return self.cache.get_certificate(cert_path)
        return None

    def get_key_by_name(self, name: str, password: Optional[bytes] = None) -> Optional[object]:
        """Get key by name."""
        for key_name, key_path in self.find_keys():
            if key_name.lower() == name.lower():
                return self.cache.get_key(key_path, password)
        return None

    def suggest_certificate_for_role(self, role: str) -> Optional[Tuple[str, Path]]:
        """Suggest a certificate for a given role."""
        certs = self.find_certificates()
        role_lower = role.lower()
        
        # Try exact role match
        for name, path in certs:
            if role_lower in name.lower():
                return (name, path)
        
        # Fall back to first available
        return certs[0] if certs else None

    def load_user_certs_from_ca(self, ca_path: Path) -> dict[str, Path]:
        """
        Load user certificates from CA directory.

        Args:
            ca_path: Path to CA directory

        Returns:
            Dictionary mapping username to certificate path
        """
        user_certs = {}
        user_certs_dir = ca_path / "issued"
        
        if user_certs_dir.exists():
            for cert_file in user_certs_dir.glob("*.p12"):
                username = cert_file.stem
                user_certs[username] = cert_file
        
        return user_certs
