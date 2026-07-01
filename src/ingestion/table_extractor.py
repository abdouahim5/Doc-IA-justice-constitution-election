"""Extraction de tableaux et chiffres depuis PDF."""

import re
from pathlib import Path

_NUMBER_RE = re.compile(
    r"(\d[\d\s]*(?:[.,]\d+)?)\s*(%|pourcent|voix|électeurs|electeurs|inscrits|votants|sièges|sieges)?",
    re.IGNORECASE,
)


def extract_tables_from_pdf(path: Path) -> list[dict]:
    """Extrait les tableaux d'un PDF avec pdfplumber."""
    try:
        import pdfplumber
    except ImportError:
        return []

    tables: list[dict] = []
    with pdfplumber.open(str(path)) as pdf:
        for page_num, page in enumerate(pdf.pages, start=1):
            for t_idx, table in enumerate(page.extract_tables() or []):
                if not table or len(table) < 2:
                    continue
                headers = [str(c or "").strip() for c in table[0]]
                rows = []
                for row in table[1:]:
                    cells = [str(c or "").strip() for c in row]
                    if any(cells):
                        rows.append(cells)
                if not rows:
                    continue
                raw = "\n".join(" | ".join(r) for r in [headers] + rows)
                tables.append({
                    "page_number": page_num,
                    "table_index": t_idx,
                    "title": headers[0] if headers else None,
                    "headers": headers,
                    "rows": rows,
                    "raw_text": raw,
                })
    return tables


def extract_facts_from_text(text: str, category: str, page: int | None = None) -> list[dict]:
    """Extrait des paires clé-valeur numériques du texte."""
    facts: list[dict] = []
    lines = text.split("\n")
    for line in lines:
        line = line.strip()
        if len(line) < 8 or len(line) > 400:
            continue
        for m in _NUMBER_RE.finditer(line):
            raw_num = m.group(1).replace(" ", "").replace(",", ".")
            try:
                num = float(raw_num)
            except ValueError:
                continue
            unit = (m.group(2) or "").strip() or None
            key_part = line[: m.start()].strip(" :-—|")[-80:]
            if not key_part:
                key_part = line[:60]
            facts.append({
                "category": category,
                "fact_key": key_part,
                "fact_value": m.group(0).strip(),
                "numeric_value": num,
                "unit": unit,
                "context": line[:300],
                "page_number": page,
            })
    return facts[:50]
