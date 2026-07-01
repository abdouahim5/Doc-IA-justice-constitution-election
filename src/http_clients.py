"""Clients HTTP avec certificats SSL fiables (Windows / Streamlit)."""

import httpx

from src.startup import ca_bundle_path, ssl_context


def new_http_clients() -> tuple[httpx.Client, httpx.AsyncClient]:
    """Clients httpx avec verification SSL explicite."""
    verify = ssl_context()
    timeout = httpx.Timeout(45.0, connect=8.0)
    return (
        httpx.Client(verify=verify, timeout=timeout),
        httpx.AsyncClient(verify=verify, timeout=timeout),
    )


def test_https() -> tuple[bool, str]:
    """Teste HTTPS vers OpenAI sans cle API (diagnostic SSL pur)."""
    try:
        client = httpx.Client(verify=ssl_context(), timeout=15.0)
        try:
            response = client.get("https://api.openai.com/v1/models")
            # 401 = connexion SSL OK, cle absente/invalide
            if response.status_code in (401, 403):
                return True, f"SSL OK (HTTP {response.status_code})"
            return True, f"SSL OK (HTTP {response.status_code})"
        finally:
            client.close()
    except Exception as e:
        return False, f"{type(e).__name__}: {e}"
