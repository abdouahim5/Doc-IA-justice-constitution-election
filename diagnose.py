#!/usr/bin/env python3
"""Diagnostic complet du projet Agent RAG."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

import src.startup  # noqa: F401

from src.config import DOCUMENTS_DIR, reload_env
from src.diagnostics import full_diagnostic, test_openai_connection
from src.retrieval.vector_store import is_index_healthy


def main():
    reload_env()
    print("=" * 50)
    print("DIAGNOSTIC AGENT RAG")
    print("=" * 50)
    for line in full_diagnostic():
        print(line)
    print("-" * 50)
    docs = list(DOCUMENTS_DIR.rglob("*")) if DOCUMENTS_DIR.exists() else []
    files = [f for f in docs if f.is_file()]
    print(f"Documents dans {DOCUMENTS_DIR}: {len(files)} fichier(s)")
    for f in files[:10]:
        print(f"  - {f.name}")
    print(f"Index ChromaDB valide: {is_index_healthy()}")
    print("-" * 50)
    ok, msg = test_openai_connection()
    print(f"RESULTAT: {'OK' if ok else 'ECHEC'}")
    print(msg)
    print("=" * 50)
    if not ok:
        sys.exit(1)


if __name__ == "__main__":
    main()
