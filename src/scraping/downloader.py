"""Téléchargement et extraction de contenu web."""

import re
import time
from pathlib import Path
from urllib.parse import urlparse

import httpx

from src.http_clients import new_http_clients
from src.scraping.sources import SourceSpec

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)
REQUEST_DELAY_SEC = 1.0


def _safe_filename(name: str) -> str:
    name = re.sub(r'[<>:"/\\|?*]', "_", name)
    return name.strip() or "document"


def _extract_html_text(html: str, url: str) -> str:
    try:
        from bs4 import BeautifulSoup
    except ImportError:
        text = re.sub(r"<script[^>]*>.*?</script>", "", html, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r"<style[^>]*>.*?</style>", "", text, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r"<[^>]+>", "\n", text)
        return re.sub(r"\n{3,}", "\n\n", text).strip()

    soup = BeautifulSoup(html, "lxml")
    for tag in soup(["script", "style", "nav", "footer", "header", "noscript", "iframe"]):
        tag.decompose()

    main = (
        soup.find("main")
        or soup.find("article")
        or soup.find(id=re.compile(r"content|main|texte", re.I))
        or soup.find(class_=re.compile(r"content|article|texte", re.I))
        or soup.body
    )
    if not main:
        return soup.get_text("\n", strip=True)

    lines: list[str] = []
    for el in main.find_all(["h1", "h2", "h3", "h4", "p", "li", "td", "th", "div"]):
        txt = el.get_text(" ", strip=True)
        if not txt or len(txt) < 3:
            continue
        if el.name in ("h1", "h2", "h3", "h4"):
            lines.append(f"\n{'#' * int(el.name[1])} {txt}\n")
        elif el.name == "li":
            lines.append(f"- {txt}")
        else:
            lines.append(txt)

    body = "\n".join(lines)
    if len(body) < 200:
        body = main.get_text("\n", strip=True)
    return re.sub(r"\n{3,}", "\n\n", body).strip()


def _discover_pdf_links(html: str, base_url: str) -> list[str]:
    try:
        from bs4 import BeautifulSoup
    except ImportError:
        return re.findall(r'href=["\']([^"\']+\.pdf[^"\']*)["\']', html, re.I)

    soup = BeautifulSoup(html, "lxml")
    links: list[str] = []
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if ".pdf" in href.lower():
            if href.startswith("http"):
                links.append(href)
            elif href.startswith("/"):
                parsed = urlparse(base_url)
                links.append(f"{parsed.scheme}://{parsed.netloc}{href}")
    return list(dict.fromkeys(links))


def download_source(
    spec: SourceSpec,
    dest_dir: Path,
    client: httpx.Client | None = None,
) -> tuple[Path | None, str | None]:
    """Télécharge une source. Retourne (chemin, erreur)."""
    dest_dir.mkdir(parents=True, exist_ok=True)
    own_client = client is None
    if own_client:
        client, _ = new_http_clients()
        client.headers["User-Agent"] = USER_AGENT

    try:
        time.sleep(REQUEST_DELAY_SEC)
        headers = {
            "Accept": "text/html,application/pdf,application/xhtml+xml,*/*;q=0.8",
            "Accept-Language": "fr-FR,fr;q=0.9",
            "Referer": "https://www.google.com/",
        }
        if "legifrance" in spec.url:
            headers["Referer"] = "https://www.legifrance.gouv.fr/"
        if "formation-civique.interieur" in spec.url:
            headers["Referer"] = "https://formation-civique.interieur.gouv.fr/"
        if "immigration.interieur" in spec.url:
            headers["Referer"] = "https://www.immigration.interieur.gouv.fr/"
        response = client.get(
            spec.url,
            follow_redirects=True,
            headers=headers,
        )
        response.raise_for_status()

        content_type = (response.headers.get("content-type") or "").lower()
        is_pdf = (
            spec.kind == "pdf"
            or "application/pdf" in content_type
            or spec.url.lower().endswith(".pdf")
        )
        is_json = (
            spec.kind == "json"
            or "application/json" in content_type
            or spec.url.lower().endswith(".json")
        )

        if is_pdf:
            fname = spec.filename or _safe_filename(spec.id) + ".pdf"
            if "/" in fname:
                path = dest_dir / fname
                path.parent.mkdir(parents=True, exist_ok=True)
            else:
                path = dest_dir / fname
            path.write_bytes(response.content)
            return path, None

        if is_json:
            fname = spec.filename or _safe_filename(spec.id) + ".json"
            if "/" in fname:
                path = dest_dir / fname
                path.parent.mkdir(parents=True, exist_ok=True)
            else:
                path = dest_dir / fname
            path.write_bytes(response.content)
            return path, None

        text = _extract_html_text(response.text, spec.url)
        if len(text) < 100:
            return None, f"Contenu HTML trop court ({len(text)} car.)"

        header = (
            f"# {spec.title}\n"
            f"Source : {spec.url}\n"
            f"Éditeur : {spec.publisher}\n"
            f"Catégorie : {spec.category}\n\n"
        )
        fname = spec.filename or _safe_filename(spec.id) + ".txt"
        if "/" in fname:
            path = dest_dir / fname
            path.parent.mkdir(parents=True, exist_ok=True)
        else:
            path = dest_dir / fname
        path.write_text(header + text, encoding="utf-8")
        return path, None

    except httpx.HTTPStatusError as e:
        return None, f"HTTP {e.response.status_code}"
    except Exception as e:
        return None, f"{type(e).__name__}: {e}"
    finally:
        if own_client:
            client.close()


def discover_extra_pdfs(
    page_url: str,
    dest_dir: Path,
    category: str,
    client: httpx.Client | None = None,
    max_pdfs: int = 5,
) -> list[Path]:
    """Découvre et télécharge des PDF liés depuis une page HTML."""
    own_client = client is None
    if own_client:
        client, _ = new_http_clients()
        client.headers["User-Agent"] = USER_AGENT

    saved: list[Path] = []
    try:
        time.sleep(REQUEST_DELAY_SEC)
        resp = client.get(page_url, follow_redirects=True)
        if resp.status_code >= 400:
            return saved
        resp.raise_for_status()
        links = _discover_pdf_links(resp.text, page_url)[:max_pdfs]
        for i, link in enumerate(links):
            try:
                time.sleep(REQUEST_DELAY_SEC)
                pdf_resp = client.get(link, follow_redirects=True)
                pdf_resp.raise_for_status()
                if "pdf" not in (pdf_resp.headers.get("content-type") or "").lower():
                    if not link.lower().endswith(".pdf"):
                        continue
                name = Path(urlparse(link).path).name or f"extra_{category}_{i}.pdf"
                path = dest_dir / _safe_filename(name)
                path.write_bytes(pdf_resp.content)
                saved.append(path)
            except Exception:
                continue
    finally:
        if own_client:
            client.close()
    return saved
