"""Lanceur Streamlit — point d'entree unique."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

import src.startup  # noqa: F401 - SSL Windows en premier

from streamlit.web import cli as stcli

if __name__ == "__main__":
    app_path = ROOT / "app.py"
    sys.argv = [
        "streamlit",
        "run",
        str(app_path),
        "--server.headless=true",
        "--server.address=127.0.0.1",
        "--browser.serverAddress=localhost",
        "--server.fileWatcherType=none",
        "--browser.gatherUsageStats=false",
    ]
    sys.exit(stcli.main())
