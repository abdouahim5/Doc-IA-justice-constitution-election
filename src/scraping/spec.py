"""Spécification d'une source officielle à scraper."""

from dataclasses import dataclass


@dataclass(frozen=True)
class SourceSpec:
    id: str
    title: str
    url: str
    category: str  # constitution | elections | justice | test_civique
    kind: str  # pdf | html | json
    filename: str | None = None
    publisher: str = ""
