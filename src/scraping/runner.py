"""Orchestration du scraping des sources officielles."""

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from src.config import DOCUMENTS_DIR
from src.http_clients import new_http_clients
from src.scraping.civic_crawler import crawl_formation_civique, discover_immigration_pdfs
from src.scraping.civic_test_sources import FORMATION_CRAWL_SEEDS
from src.scraping.justice_crawler import crawl_justice_pages
from src.scraping.datagouv import download_datagouv
from src.scraping.downloader import discover_extra_pdfs, download_source
from src.scraping.sources import SourceSpec, sources_by_category

SCRAPED_SUBDIR = "sources_officielles"


@dataclass
class ScrapeItemResult:
    source_id: str
    title: str
    category: str
    path: str | None = None
    error: str | None = None


@dataclass
class ScrapeResult:
    downloaded: list[ScrapeItemResult] = field(default_factory=list)
    failed: list[ScrapeItemResult] = field(default_factory=list)
    extra_pdfs: list[str] = field(default_factory=list)
    civic_crawled: int = 0
    justice_crawled: int = 0
    manifest_path: str | None = None

    @property
    def ok_count(self) -> int:
        return len(self.downloaded)

    @property
    def fail_count(self) -> int:
        return len(self.failed)


def _output_dir(base: Path | None = None) -> Path:
    root = base or DOCUMENTS_DIR
    return root / SCRAPED_SUBDIR


def scrape_all(
    category: str | None = None,
    output_dir: Path | None = None,
    discover_pdfs: bool = True,
    include_datagouv: bool = True,
    include_large_csv: bool = True,
    crawl_formation: bool = True,
    crawl_justice: bool = True,
    max_civic_pages: int = 150,
    max_justice_pages: int = 80,
) -> ScrapeResult:
    """Télécharge toutes les sources officielles cataloguées."""
    dest = output_dir or _output_dir()
    dest.mkdir(parents=True, exist_ok=True)

    specs = sources_by_category(category)
    result = ScrapeResult()
    client, _ = new_http_clients()

    try:
        for spec in specs:
            path, err = download_source(spec, dest, client=client)
            item = ScrapeItemResult(
                source_id=spec.id,
                title=spec.title,
                category=spec.category,
                path=str(path) if path else None,
                error=err,
            )
            if path:
                result.downloaded.append(item)
            else:
                result.failed.append(item)

        if category in (None, "test_civique"):
            if discover_pdfs:
                for item in discover_immigration_pdfs(dest, client):
                    if item.path:
                        result.downloaded.append(ScrapeItemResult(
                            source_id=item.source_id,
                            title=item.title,
                            category="test_civique",
                            path=item.path,
                        ))
                    elif item.error:
                        result.failed.append(ScrapeItemResult(
                            source_id=item.source_id,
                            title=item.title,
                            category="test_civique",
                            error=item.error,
                        ))

            if crawl_formation:
                crawl_items = crawl_formation_civique(
                    dest,
                    client,
                    seeds=FORMATION_CRAWL_SEEDS,
                    max_pages=max_civic_pages,
                )
                for item in crawl_items:
                    row = ScrapeItemResult(
                        source_id=item.source_id,
                        title=item.title,
                        category="test_civique",
                        path=item.path,
                        error=item.error,
                    )
                    if item.path:
                        result.downloaded.append(row)
                        result.civic_crawled += 1
                    else:
                        result.failed.append(row)

        if category in (None, "justice") and crawl_justice:
            justice_items = crawl_justice_pages(
                dest, client, max_pages=max_justice_pages,
            )
            for item in justice_items:
                row = ScrapeItemResult(
                    source_id=item.source_id,
                    title=item.title,
                    category="justice",
                    path=item.path,
                    error=item.error,
                )
                if item.path:
                    result.downloaded.append(row)
                    result.justice_crawled += 1
                else:
                    result.failed.append(row)

        if discover_pdfs and category in (None, "elections"):
            for portal in (
                "https://www.elections.interieur.gouv.fr/",
                "https://www.vie-publique.fr/themes/elections",
            ):
                extras = discover_extra_pdfs(
                    portal, dest, category or "elections", client=client, max_pdfs=3
                )
                result.extra_pdfs.extend(str(p) for p in extras)
                for p in extras:
                    result.downloaded.append(ScrapeItemResult(
                        source_id=f"discovered_{p.stem}",
                        title=p.name,
                        category="elections",
                        path=str(p),
                    ))
    finally:
        client.close()

    if include_datagouv and category in (None, "elections"):
        dg_ok, dg_fail = download_datagouv(dest, include_large_csv=include_large_csv)
        for item in dg_ok:
            result.downloaded.append(ScrapeItemResult(
                source_id=item.source_id,
                title=item.title,
                category=item.category,
                path=item.path,
            ))
        for item in dg_fail:
            result.failed.append(ScrapeItemResult(
                source_id=item.source_id,
                title=item.title,
                category=item.category,
                error=item.error,
            ))

    manifest = {
        "scraped_at": datetime.now(timezone.utc).isoformat(),
        "category_filter": category,
        "downloaded": [item.__dict__ for item in result.downloaded],
        "failed": [item.__dict__ for item in result.failed],
        "extra_pdfs": result.extra_pdfs,
        "civic_crawled": result.civic_crawled,
        "justice_crawled": result.justice_crawled,
    }
    manifest_path = dest / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    result.manifest_path = str(manifest_path)
    return result
