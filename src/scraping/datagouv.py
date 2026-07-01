"""Téléchargement open data élections depuis data.gouv.fr."""

import time
from dataclasses import dataclass
from pathlib import Path

import httpx

from src.http_clients import new_http_clients
from src.scraping.downloader import USER_AGENT, _safe_filename

# Ressources directes (Ministère de l'Intérieur / pipeline open data)
DIRECT_RESOURCES: list[dict] = [
    {
        "id": "pres_2022_t1_france",
        "title": "Présidentielle 2022 — 1er tour (France entière)",
        "url": "https://static.data.gouv.fr/resources/election-presidentielle-des-10-et-24-avril-2022-resultats-definitifs-du-1er-tour/20220414-152200/resultats-par-niveau-fe-t1-france-entiere.txt",
        "filename": "presidentielle_2022_t1_france.txt",
        "category": "elections",
    },
    {
        "id": "pres_2022_t2_france",
        "title": "Présidentielle 2022 — 2nd tour (France entière)",
        "url": "https://static.data.gouv.fr/resources/election-presidentielle-des-10-et-24-avril-2022-resultats-definitifs-du-2nd-tour/20220428-141900/resultats-par-niveau-fe-t2-france-entiere.txt",
        "filename": "presidentielle_2022_t2_france.txt",
        "category": "elections",
    },
    {
        "id": "pres_2022_t1_departements",
        "title": "Présidentielle 2022 — 1er tour par département",
        "url": "https://static.data.gouv.fr/resources/election-presidentielle-des-10-et-24-avril-2022-resultats-definitifs-du-1er-tour/20220414-152356/resultats-par-niveau-dpt-t1-france-entiere.txt",
        "filename": "presidentielle_2022_t1_par_departement.txt",
        "category": "elections",
    },
    {
        "id": "pres_2022_t2_departements",
        "title": "Présidentielle 2022 — 2nd tour par département",
        "url": "https://static.data.gouv.fr/resources/election-presidentielle-des-10-et-24-avril-2022-resultats-definitifs-du-2nd-tour/20220428-142127/resultats-par-niveau-dpt-t2-france-entiere.txt",
        "filename": "presidentielle_2022_t2_par_departement.txt",
        "category": "elections",
    },
    {
        "id": "pres_2022_t1_regions",
        "title": "Présidentielle 2022 — 1er tour par région",
        "url": "https://static.data.gouv.fr/resources/election-presidentielle-des-10-et-24-avril-2022-resultats-definitifs-du-1er-tour/20220414-152331/resultats-par-niveau-reg-t1-france-entiere.txt",
        "filename": "presidentielle_2022_t1_par_region.txt",
        "category": "elections",
    },
    {
        "id": "elections_dictionnaire_nuances",
        "title": "Dictionnaire des nuances politiques (Intérieur, fév. 2026)",
        "url": "https://static.data.gouv.fr/resources/donnees-des-elections-agregees/20260324-132009/nuances.csv",
        "filename": "dictionnaire_nuances_politiques.csv",
        "category": "elections",
    },
    # --- Élections 2024 (résultats officiels Intérieur) ---
    {
        "id": "euro_2024_departements",
        "title": "Européennes 2024 — résultats par département (CSV)",
        "url": "https://static.data.gouv.fr/resources/resultats-des-elections-europeennes-du-9-juin-2024/20240613-154909/resultats-definitifs-par-departement.csv",
        "filename": "europeennes_2024_par_departement.csv",
        "category": "elections",
    },
    {
        "id": "euro_2024_regions",
        "title": "Européennes 2024 — résultats par région (CSV)",
        "url": "https://static.data.gouv.fr/resources/resultats-des-elections-europeennes-du-9-juin-2024/20240613-154915/resultats-definitifs-par-region.csv",
        "filename": "europeennes_2024_par_region.csv",
        "category": "elections",
    },
    {
        "id": "leg_2024_t1_departements",
        "title": "Législatives 2024 — 1er tour par département (CSV)",
        "url": "https://static.data.gouv.fr/resources/elections-legislatives-des-30-juin-et-7-juillet-2024-resultats-definitifs-du-1er-tour/20240710-171330/resultats-definitifs-par-departements.csv",
        "filename": "legislatives_2024_t1_par_departement.csv",
        "category": "elections",
    },
    {
        "id": "leg_2024_t1_regions",
        "title": "Législatives 2024 — 1er tour par région (CSV)",
        "url": "https://static.data.gouv.fr/resources/elections-legislatives-des-30-juin-et-7-juillet-2024-resultats-definitifs-du-1er-tour/20240710-171318/resultats-definitifs-par-regions.csv",
        "filename": "legislatives_2024_t1_par_region.csv",
        "category": "elections",
    },
    {
        "id": "leg_2024_t2_france",
        "title": "Législatives 2024 — 2nd tour France entière (CSV)",
        "url": "https://static.data.gouv.fr/resources/elections-legislatives-des-30-juin-et-7-juillet-2024-resultats-definitifs-du-2nd-tour/20240710-170713/resultats-definitifs-france-entiere.csv",
        "filename": "legislatives_2024_t2_france.csv",
        "category": "elections",
    },
    {
        "id": "leg_2024_t2_departements",
        "title": "Législatives 2024 — 2nd tour par département (CSV)",
        "url": "https://static.data.gouv.fr/resources/elections-legislatives-des-30-juin-et-7-juillet-2024-resultats-definitifs-du-2nd-tour/20240710-170553/resultats-definitifs-par-departement.csv",
        "filename": "legislatives_2024_t2_par_departement.csv",
        "category": "elections",
    },
]

# Jeux de données à résoudre via API (prend la ressource CSV/TXT la plus récente)
DATASET_SLUGS: list[dict] = [
    {
        "slug": "donnees-des-elections-agregees",
        "title": "Élections agrégées — résultats généraux (échantillon)",
        "filename": "elections_agregees_general.csv",
        "format": "csv",
        "url_contains": "general_results.csv",
        "max_bytes": 15_000_000,
        "category": "elections",
    },
]


@dataclass
class DataGouvItem:
    source_id: str
    title: str
    category: str
    path: str | None = None
    error: str | None = None


def _resolve_dataset_resource(slug: str, fmt: str, url_contains: str) -> str | None:
    client, _ = new_http_clients()
    try:
        r = client.get(f"https://www.data.gouv.fr/api/1/datasets/{slug}/")
        r.raise_for_status()
        resources = r.json().get("resources", [])
        candidates = [
            res for res in resources
            if (res.get("format") or "").lower() == fmt.lower()
            and url_contains in (res.get("url") or "")
        ]
        if not candidates:
            candidates = [res for res in resources if url_contains in (res.get("url") or "")]
        if not candidates:
            return None
        candidates.sort(key=lambda x: x.get("last_modified") or "", reverse=True)
        return candidates[0].get("url")
    except Exception:
        return None
    finally:
        client.close()


def _download_file(
    client: httpx.Client,
    url: str,
    dest: Path,
    max_bytes: int | None = None,
) -> None:
    time.sleep(0.5)
    with client.stream("GET", url, follow_redirects=True) as response:
        response.raise_for_status()
        dest.parent.mkdir(parents=True, exist_ok=True)
        written = 0
        with dest.open("wb") as f:
            for chunk in response.iter_bytes(65536):
                f.write(chunk)
                written += len(chunk)
                if max_bytes and written > max_bytes:
                    break


def _make_csv_summary(csv_path: Path, summary_path: Path, max_rows: int = 500) -> None:
    """Crée un résumé texte des premières lignes + agrégats par id_election."""
    lines_out: list[str] = [
        f"# Résumé : {csv_path.name}",
        f"Source : data.gouv.fr",
        "",
    ]
    try:
        import csv
        from collections import defaultdict

        counts: dict[str, int] = defaultdict(int)
        with csv_path.open(encoding="utf-8", errors="replace") as f:
            reader = csv.DictReader(f, delimiter=";")
            fieldnames = reader.fieldnames or []
            lines_out.append(f"Colonnes : {', '.join(fieldnames[:12])}")
            lines_out.append("")
            for i, row in enumerate(reader):
                eid = row.get("id_election") or row.get("election") or "?"
                counts[eid] += 1
                if i < 30:
                    lines_out.append(
                        f"- {eid} | inscrits={row.get('inscrits','?')} "
                        f"votants={row.get('votants','?')} exprimés={row.get('exprimes','?')}"
                    )
                if i >= max_rows:
                    break
        lines_out.append("")
        lines_out.append("## Répartition par scrutin (échantillon)")
        for eid, n in sorted(counts.items(), key=lambda x: -x[1])[:25]:
            lines_out.append(f"- {eid}: {n} lignes")
    except Exception as e:
        lines_out.append(f"(résumé partiel : {e})")
        with csv_path.open(encoding="utf-8", errors="replace") as f:
            for i, line in enumerate(f):
                if i >= 50:
                    break
                lines_out.append(line.rstrip())
    summary_path.write_text("\n".join(lines_out), encoding="utf-8")


def download_datagouv(
    dest_dir: Path,
    include_large_csv: bool = True,
) -> tuple[list[DataGouvItem], list[DataGouvItem]]:
    """Télécharge les jeux data.gouv.fr. Retourne (ok, failed)."""
    data_dir = dest_dir / "donnees"
    data_dir.mkdir(parents=True, exist_ok=True)
    ok: list[DataGouvItem] = []
    failed: list[DataGouvItem] = []

    client, _ = new_http_clients()
    client.headers["User-Agent"] = USER_AGENT

    try:
        for spec in DIRECT_RESOURCES:
            item = DataGouvItem(
                source_id=spec["id"],
                title=spec["title"],
                category=spec["category"],
            )
            dest = data_dir / spec["filename"]
            try:
                _download_file(client, spec["url"], dest)
                header = (
                    f"# {spec['title']}\n"
                    f"Source : {spec['url']}\n"
                    f"Éditeur : data.gouv.fr / Ministère de l'Intérieur\n\n"
                )
                if dest.suffix.lower() == ".txt":
                    body = dest.read_text(encoding="utf-8", errors="replace")
                    dest.write_text(header + body, encoding="utf-8")
                elif dest.suffix.lower() == ".csv":
                    summary = data_dir / (dest.stem + "_resume.txt")
                    _make_csv_summary(dest, summary, max_rows=800)
                    ok.append(DataGouvItem(
                        source_id=spec["id"] + "_resume",
                        title=spec["title"] + " (résumé)",
                        category=spec["category"],
                        path=str(summary),
                    ))
                item.path = str(dest)
                ok.append(item)
            except Exception as e:
                item.error = str(e)
                failed.append(item)

        if include_large_csv:
            for ds in DATASET_SLUGS:
                item = DataGouvItem(
                    source_id=ds["slug"],
                    title=ds["title"],
                    category=ds["category"],
                )
                url = _resolve_dataset_resource(ds["slug"], ds["format"], ds["url_contains"])
                if not url:
                    item.error = "Ressource introuvable via API"
                    failed.append(item)
                    continue
                dest = data_dir / _safe_filename(ds["filename"])
                try:
                    _download_file(client, url, dest, max_bytes=ds.get("max_bytes"))
                    summary = data_dir / (dest.stem + "_resume.txt")
                    _make_csv_summary(dest, summary)
                    item.path = str(dest)
                    ok.append(item)
                    ok.append(DataGouvItem(
                        source_id=ds["slug"] + "_resume",
                        title=ds["title"] + " (résumé)",
                        category=ds["category"],
                        path=str(summary),
                    ))
                except Exception as e:
                    item.error = str(e)
                    failed.append(item)
    finally:
        client.close()

    return ok, failed
