"""Point d'entree unique : SSL Windows + variables d'environnement.

Importer ce module EN PREMIER dans tout script (app.py, main.py, run_app.py).
"""

import os
import ssl
import sys
from pathlib import Path

import certifi

_ROOT = Path(__file__).resolve().parent.parent
_CA_BUNDLE = certifi.where()

# Certificats — force a chaque demarrage (critique pour le sous-processus Streamlit)
os.environ["SSL_CERT_FILE"] = _CA_BUNDLE
os.environ["REQUESTS_CA_BUNDLE"] = _CA_BUNDLE
os.environ["CURL_CA_BUNDLE"] = _CA_BUNDLE

# Utiliser le magasin de certificats Windows (corrige CERTIFICATE_VERIFY_FAILED)
try:
    import truststore

    truststore.inject_into_ssl()
    _USING_TRUSTSTORE = True
except ImportError:
    _USING_TRUSTSTORE = False

try:
    import pip_system_certs.wrapt_requests  # noqa: F401
except ImportError:
    if sys.platform == "win32":
        print("[WARN] pip install pip-system-certs truststore certifi")

# Contexte SSL partage pour httpx / OpenAI
_SSL_CONTEXT = ssl.create_default_context(cafile=_CA_BUNDLE)
if _USING_TRUSTSTORE:
    try:
        _SSL_CONTEXT = truststore.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    except Exception:
        pass


def ssl_context() -> ssl.SSLContext:
    """Contexte SSL verifie pour les clients HTTP."""
    return _SSL_CONTEXT


def ca_bundle_path() -> str:
    return _CA_BUNDLE


def project_root() -> Path:
    return _ROOT
