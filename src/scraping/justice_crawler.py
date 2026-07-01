"""Crawler récursif — service-public Justice et justice.gouv.fr (droit pénal)."""

from __future__ import annotations

import re
import time
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urljoin, urlparse, urlunparse

import httpx

from src.scraping.downloader import USER_AGENT, _extract_html_text, _safe_filename
from src.scraping.justice_sources import JUSTICE_CRAWL_SEEDS

REQUEST_DELAY_SEC = 1.0

_SP_HOST = "www.service-public.gouv.fr"
_JG_HOST = "www.justice.gouv.fr"

_SP_PATH_RE = re.compile(r"^/particuliers/vosdroits/F\d+", re.I)
_JG_PATH_RE = re.compile(r"^/justice-france/", re.I)


@dataclass
class JusticeCrawlItem:
    source_id: str
    title: str
    path: str | None = None
    error: str | None = None


def _normalize_url(url: str) -> str:
    parsed = urlparse(url)
    path = parsed.path.rstrip("/") + "/"
    return urlunparse((parsed.scheme, parsed.netloc, path, "", "", ""))


def _url_to_filename(url: str) -> str:
    parsed = urlparse(url)
    path = parsed.path.strip("/").replace("/", "_")
    if not path:
        path = "accueil"
    path = path.replace("é", "e").replace("è", "e").replace("à", "a")
    return _safe_filename(f"j_{path}.txt")


def _is_crawlable(url: str) -> bool:
    parsed = urlparse(url)
    host = parsed.netloc
    if host not in (_SP_HOST, _JG_HOST):
        return False
    low = url.lower()
    if any(x in low for x in (".pdf", ".jpg", ".png", ".svg", ".css", ".js", "mailto:", "#")):
        return False
    if host == _SP_HOST:
        return bool(_SP_PATH_RE.match(parsed.path))
    return bool(_JG_PATH_RE.match(parsed.path))


def _extract_links(html: str, base_url: str) -> list[str]:
    try:
        from bs4 import BeautifulSoup
    except ImportError:
        return []

    soup = BeautifulSoup(html, "lxml")
    found: list[str] = []
    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        if not href or href.startswith("#"):
            continue
        full = urljoin(base_url, href)
        full = _normalize_url(full.split("#")[0])
        if _is_crawlable(full):
            found.append(full)
    return list(dict.fromkeys(found))


def _headers(url: str) -> dict[str, str]:
    parsed = urlparse(url)
    referer = f"https://{parsed.netloc}/"
    return {
        "Accept": "text/html,application/xhtml+xml,*/*;q=0.8",
        "Accept-Language": "fr-FR,fr;q=0.9",
        "Referer": referer,
        "User-Agent": USER_AGENT,
    }


def crawl_justice_pages(
    dest_dir: Path,
    client: httpx.Client,
    seeds: list[str] | None = None,
    max_pages: int = 80,
) -> list[JusticeCrawlItem]:
    """Parcourt les pages justice service-public et justice.gouv.fr."""
    out_dir = dest_dir / "justice" / "pages_crawlees"
    out_dir.mkdir(parents=True, exist_ok=True)

    queue: list[str] = [_normalize_url(u) for u in (seeds or JUSTICE_CRAWL_SEEDS)]
    seen: set[str] = set()
    results: list[JusticeCrawlItem] = []

    while queue and len(seen) < max_pages:
        url = queue.pop(0)
        if url in seen:
            continue
        seen.add(url)

        try:
            time.sleep(REQUEST_DELAY_SEC)
            resp = client.get(url, follow_redirects=True, headers=_headers(url))
            if resp.status_code >= 400:
                results.append(JusticeCrawlItem(
                    source_id=f"jcrawl_{urlparse(url).path.strip('/').replace('/', '_') or 'root'}",
                    title=url,
                    error=f"HTTP {resp.status_code}",
                ))
                continue

            text = _extract_html_text(resp.text, url)
            if len(text) < 80:
                results.append(JusticeCrawlItem(
                    source_id=f"jcrawl_{len(seen)}",
                    title=url,
                    error=f"Contenu trop court ({len(text)} car.)",
                ))
                continue

            title_match = re.search(r"^#\s+(.+)$", text, re.M)
            title = title_match.group(1).strip() if title_match else url

            header = (
                f"# {title}\n"
                f"Source : {url}\n"
                f"Catégorie : justice\n\n"
            )
            fname = _url_to_filename(url)
            path = out_dir / fname
            path.write_text(header + text, encoding="utf-8")
            results.append(JusticeCrawlItem(
                source_id=f"jcrawl_{path.stem}",
                title=title[:120],
                path=str(path),
            ))

            for link in _extract_links(resp.text, url):
                if link not in seen and link not in queue:
                    queue.append(link)

        except httpx.HTTPStatusError as e:
            results.append(JusticeCrawlItem(
                source_id=f"jcrawl_err_{len(seen)}",
                title=url,
                error=f"HTTP {e.response.status_code}",
            ))
        except Exception as e:
            results.append(JusticeCrawlItem(
                source_id=f"jcrawl_err_{len(seen)}",
                title=url,
                error=f"{type(e).__name__}: {e}",
            ))

    return results
