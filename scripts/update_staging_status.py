#!/usr/bin/env python3
"""Met à jour deploy/staging.metrics.json et les blocs STAGING dans README.md / docs/STAGING.md."""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS_DIR = ROOT / "data" / "documents"
EXT = {".pdf", ".txt", ".md", ".docx", ".csv", ".json"}
MARKER_START = "<!-- STAGING:AUTO:START -->"
MARKER_END = "<!-- STAGING:AUTO:END -->"


def _count_corpus_files() -> dict[str, int]:
    counts = {"total": 0, "constitution": 0, "elections": 0, "justice": 0, "test_civique": 0, "other": 0}
    for path in DOCS_DIR.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in EXT:
            continue
        if path.name == "manifest.json":
            continue
        rel = path.relative_to(DOCS_DIR).as_posix()
        counts["total"] += 1
        if "/justice/" in rel or rel.startswith("sources_officielles/justice_"):
            counts["justice"] += 1
        elif "/test_civique/" in rel:
            counts["test_civique"] += 1
        elif any(
            k in rel.lower()
            for k in ("constitution", "declaration_1789", "preambule", "charte_environnement", "qpc")
        ):
            counts["constitution"] += 1
        elif any(
            k in rel.lower()
            for k in ("election", "insee", "vote", "scrutin", "referendum", "donnees/", "calendrier")
        ):
            counts["elections"] += 1
        else:
            counts["other"] += 1
    return counts


def _pg_stats() -> dict | None:
    try:
        from src.db.engine import check_connection, get_session
        from src.db.repository import CorpusRepository

        ok, _ = check_connection()
        if not ok:
            return None
        session = get_session()
        stats = CorpusRepository(session).get_stats()
        session.close()
        return stats
    except Exception:
        return None


def _load_staging_env() -> dict[str, str]:
    env_path = ROOT / "deploy" / "staging.env"
    out: dict[str, str] = {}
    if not env_path.exists():
        return out
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, _, v = line.partition("=")
        out[k.strip()] = v.strip()
    return out


def collect_metrics() -> dict:
    env = _load_staging_env()
    files = _count_corpus_files()
    pg = _pg_stats() or {}

    chunks = pg.get("total_chunks")
    sources_pg = pg.get("total_sources")
    cached = pg.get("cached_queries", 0)

    return {
        "updated_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        "server": env.get("STAGING_SERVER", "Hetzner CX22 — Ubuntu 24.04"),
        "ip": env.get("STAGING_IP", "—"),
        "domain": env.get("STAGING_DOMAIN", "—"),
        "status": env.get("STAGING_STATUS", "en_attente"),
        "branch": env.get("STAGING_BRANCH", "main"),
        "url_app": env.get("STAGING_URL_APP", "http://IP_OU_DOMAINE"),
        "url_health": env.get("STAGING_URL_HEALTH", "http://IP_OU_DOMAINE/_stcore/health"),
        "files_total": files["total"],
        "files_by_category": files,
        "chunks_indexed": chunks if chunks is not None else "—",
        "sources_pg": sources_pg if sources_pg is not None else "—",
        "cached_queries": cached,
        "phase": "Phase 2 — Multi-Agents (6 agents)",
        "routing": "Classifier hybride (mots-clés + historique + thème)",
        "synthesis_model": "gpt-4o-mini",
        "embeddings": "text-embedding-3-small",
        "vector_primary": "PostgreSQL pgvector",
        "vector_fallback": "ChromaDB (./data/vectorstore)",
    }


def _status_badge(status: str) -> str:
    if status == "en_ligne":
        return "🟢 En ligne"
    if status == "maintenance":
        return "🟠 Maintenance"
    return "🟡 En attente de déploiement"


def _progress_bar(current: int, total: int, width: int = 20) -> str:
    if total <= 0:
        return ""
    filled = round(width * current / total)
    return "█" * filled + "░" * (width - filled)


def render_block(m: dict) -> str:
    files = m["files_by_category"]
    active = m["sources_pg"] if isinstance(m["sources_pg"], int) else m["files_total"]
    target = max(m["files_total"], 1)
    pct = round(100 * (active if isinstance(active, int) else m["files_total"]) / target)

    chunks_display = (
        f"{m['chunks_indexed']:,}".replace(",", " ")
        if isinstance(m["chunks_indexed"], int)
        else f"— *(lancer `pg-ingest`)*"
    )
    sources_display = (
        f"{m['sources_pg']} / {m['files_total']}"
        if isinstance(m["sources_pg"], int)
        else f"{m['files_total']} fichiers *(PG après ingestion)*"
    )

    return f"""{MARKER_START}
**Dernière mise à jour :** {m["updated_at"]} · Branche `{m["branch"]}` · [Détails complets](docs/STAGING.md)

## Environnement déployé

| | |
|---|---|
| **Serveur** | {m["server"]} |
| **IP** | `{m["ip"]}` |
| **Domaine** | `{m["domain"]}` |
| **Stack** | Docker Compose (caddy + app Streamlit + postgres pgvector) |
| **Statut** | {_status_badge(m["status"])} |

| Interface | URL |
|-----------|-----|
| **Application** | {m["url_app"]} |
| **France Civique** (multi-agent) | {m["url_app"]} → menu *France Civique* |
| **Test civique** | {m["url_app"]} → menu *Test civique* |
| **Admin / diagnostic** | {m["url_app"]} → menu *Configuration* |
| **Health** | {m["url_health"]} |

## État du déploiement

| Métrique | Valeur |
|----------|--------|
| **Chunks indexés** | {chunks_display} |
| **Sources actives** | {sources_display} `{_progress_bar(min(active if isinstance(active, int) else m['files_total'], target), target, 12)}` {pct}% |
| **Par catégorie** | constitution {files["constitution"]} · élections {files["elections"]} · justice {files["justice"]} · test civique {files["test_civique"]} |
| **Phase déployée** | {m["phase"]} |
| **Modèle routing** | `{m["routing"]}` |
| **Modèle synthesis** | `{m["synthesis_model"]}` |
| **Embeddings** | `{m["embeddings"]}` |
| **Vector store principal** | `{m["vector_primary"]}` |
| **Vector store secours** | `{m["vector_fallback"]}` |
| **Réponses en cache** | {m["cached_queries"] if m["cached_queries"] else "—"} |

## Architecture déployée

```
                         Internet
                             │
                             ▼
                   Caddy :80 / :443
                   (ou IP:8501 direct)
                             │
                             ▼
                   Streamlit :8501  (docia-app)
                   8 pages · FR/EN
                             │
                   MultiAgentOrchestrator
                             │
              ┌──────────────┴──────────────┐
              │  Classifier + resolve_topic  │
              │  (historique · thème actif)    │
              └──────────────┬──────────────┘
                             │
         ┌───────────────────┼───────────────────┐
         ▼                   ▼                   ▼
  constitution          elections            justice
  test_civique            data              general
         │                   │                   │
         └───────────────────┼───────────────────┘
                             ▼
              Retrieval hybride par agent
              · vecteurs cosine (pgvector)
              · ILIKE + pg_trgm
              · patterns (articles, dates, pénal)
              · query_cache
                             │
                             ▼
              Synthesis LLM (gpt-4o-mini)
              réponses sourcées + citations
                             │
              ┌──────────────┴──────────────┐
              ▼                             ▼
     PostgreSQL pgvector              ChromaDB local
     (principal · réseau interne)     (secours si PG down)
```

> Mettre à jour : `py scripts/update_staging_status.py` · config VPS : `deploy/staging.env`
{MARKER_END}"""


def patch_file(path: Path, block: str) -> bool:
    text = path.read_text(encoding="utf-8")
    pattern = re.compile(
        re.escape(MARKER_START) + r".*?" + re.escape(MARKER_END),
        re.DOTALL,
    )
    if not pattern.search(text):
        return False
    path.write_text(pattern.sub(block, text), encoding="utf-8")
    return True


def main() -> None:
    metrics = collect_metrics()
    (ROOT / "deploy" / "staging.metrics.json").write_text(
        json.dumps(metrics, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    block = render_block(metrics)
    for rel in ("README.md", "docs/STAGING.md"):
        path = ROOT / rel
        if patch_file(path, block):
            print(f"OK  {rel}")
        else:
            print(f"SKIP {rel} (marqueurs absents)")
    print(f"Metrics -> deploy/staging.metrics.json ({metrics['files_total']} fichiers corpus)")


if __name__ == "__main__":
    main()
