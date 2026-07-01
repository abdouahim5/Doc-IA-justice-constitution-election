#!/usr/bin/env python3
"""Interface en ligne de commande pour l'agent RAG."""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import src.startup  # noqa: F401 - SSL Windows

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table

from src.agent import RAGAgent
from src.config import DOCUMENTS_DIR, get_llm_status

console = Console(force_terminal=True, legacy_windows=False)


def _print_llm_banner() -> bool:
    """Affiche l'etat LLM. Retourne False si configuration invalide."""
    status = get_llm_status()
    if status["ready"]:
        console.print(f"[dim]LLM : {status['message']}[/]")
        return True
    console.print(f"[bold red]{status['message']}[/]")
    console.print("Corrigez le fichier .env puis relancez la commande.")
    return False


def _require_index(agent: RAGAgent) -> bool:
    stats = agent.get_stats()
    if stats["chunks_indexed"] == 0:
        console.print("[yellow]Aucun document indexé. Lancez d'abord :[/]")
        console.print("  python main.py index")
        return False
    return True


def cmd_index(args):
    """Indexe les documents."""
    if not _print_llm_banner():
        return

    agent = RAGAgent()
    directory = Path(args.dir) if args.dir else DOCUMENTS_DIR

    console.print(f"[bold blue]Indexation depuis :[/] {directory}")
    result = agent.index_documents_detailed(directory)

    if result.errors:
        for err in result.errors:
            console.print(f"[yellow]WARN[/] {err}")

    if result.chunks == 0:
        console.print("[yellow]Aucun document trouvé.[/]")
        console.print(f"Placez vos fichiers (PDF, TXT, MD, DOCX) dans : {directory}")
        return

    console.print(f"[bold green]OK - {result.chunks} chunks indexes avec succes[/]")


def cmd_chat(args):
    """Mode conversation interactif."""
    if not _print_llm_banner():
        return

    agent = RAGAgent()
    if not _require_index(agent):
        return

    stats = agent.get_stats()
    console.print(Panel(
        f"[bold]Agent RAG[/] — {stats['chunks_indexed']} chunks indexés\n"
        "Tapez votre question (ou 'quit' pour quitter, 'clear' pour effacer la mémoire)",
        title="Assistant Documentaire",
    ))

    while True:
        try:
            question = console.input("\n[bold cyan]Vous :[/] ").strip()
        except (KeyboardInterrupt, EOFError):
            console.print("\n[dim]Au revoir ![/]")
            break

        if not question:
            continue
        if question.lower() in ("quit", "exit", "q"):
            console.print("[dim]Au revoir ![/]")
            break
        if question.lower() == "clear":
            agent.clear_memory()
            console.print("[dim]Mémoire effacée.[/]")
            continue

        try:
            with console.status("[bold green]Réflexion en cours..."):
                response = agent.query(question)
        except RuntimeError as e:
            console.print(f"[bold red]Erreur :[/] {e}")
            continue

        console.print("\n[bold green]Agent :[/]")
        console.print(Markdown(response.answer))

        if response.sources:
            table = Table(title="Sources", show_header=True)
            table.add_column("Fichier", style="cyan")
            table.add_column("Extrait", style="dim")
            for src in response.sources:
                table.add_row(src["file"], src["excerpt"][:150])
            console.print(table)


def cmd_ask(args):
    """Pose une question unique."""
    if not _print_llm_banner():
        return

    agent = RAGAgent()
    if not _require_index(agent):
        return

    try:
        response = agent.query(args.question)
    except RuntimeError as e:
        console.print(f"[bold red]Erreur :[/] {e}")
        sys.exit(1)

    console.print(Markdown(response.answer))


def cmd_search(args):
    """Recherche un mot dans les documents."""
    agent = RAGAgent()
    if not _require_index(agent):
        return

    response = agent.search_word(args.mot)
    console.print(Markdown(response.answer))


def cmd_stats(args):
    """Affiche les statistiques."""
    agent = RAGAgent()
    stats = agent.get_stats()
    llm = get_llm_status()
    console.print(Panel(
        f"Chunks indexés : [bold]{stats['chunks_indexed']}[/]\n"
        f"Répertoire docs : {stats['documents_dir']}\n"
        f"LLM : {llm['message']}",
        title="Statistiques",
    ))


def cmd_clear(args):
    """Supprime l'index."""
    agent = RAGAgent()
    agent.clear_index()
    console.print("[bold green]OK - Index supprime[/]")


def cmd_pg_init(args):
    """Initialise PostgreSQL (tables + extensions)."""
    from src.db.engine import check_connection, init_db

    console.print("[bold blue]Initialisation PostgreSQL...[/]")
    try:
        init_db()
        ok, msg = check_connection()
        console.print(f"[bold green]{'OK' if ok else 'WARN'}[/] {msg}")
    except Exception as e:
        console.print(f"[bold red]Erreur :[/] {e}")
        console.print("Lancez d'abord : docker compose up -d")
        sys.exit(1)


def cmd_pg_ingest(args):
    """Ingère les documents dans PostgreSQL (texte, tableaux, chiffres)."""
    if not _print_llm_banner():
        return

    from src.ingestion.pg_pipeline import ingest_directory

    directory = Path(args.dir) if args.dir else DOCUMENTS_DIR
    path_filter = "justice" if getattr(args, "justice_only", False) else None
    if path_filter and not args.dir:
        directory = DOCUMENTS_DIR
    console.print(f"[bold blue]Ingestion PostgreSQL depuis :[/] {directory}")
    if path_filter:
        console.print(f"[dim]Filtre : chemins contenant « {path_filter} »[/]")
    try:
        with console.status("[bold green]Extraction + embeddings..."):
            stats = ingest_directory(directory, path_filter=path_filter)
    except Exception as e:
        console.print(f"[bold red]Erreur :[/] {e}")
        sys.exit(1)

    if stats.get("errors"):
        for err in stats["errors"]:
            console.print(f"[yellow]WARN[/] {err}")

    table = Table(title="Ingestion PostgreSQL", show_header=True)
    table.add_column("Métrique", style="cyan")
    table.add_column("Valeur", style="green")
    for k, v in stats.items():
        if k != "errors":
            table.add_row(k, str(v))
    console.print(table)


def cmd_pg_stats(args):
    """Statistiques du corpus PostgreSQL."""
    from src.db.engine import check_connection, get_session
    from src.db.repository import CorpusRepository

    ok, msg = check_connection()
    if not ok:
        console.print(f"[bold red]{msg}[/]")
        console.print("Lancez : docker compose up -d && python main.py pg-init")
        return

    session = get_session()
    stats = CorpusRepository(session).get_stats()
    session.close()
    console.print(Panel(
        "\n".join(f"{k} : [bold]{v}[/]" for k, v in stats.items()),
        title=f"PostgreSQL — {msg}",
    ))


def cmd_pg_cache_clear(args):
    """Vide le cache des réponses (query_cache)."""
    from src.db.engine import check_connection, get_session
    from src.db.repository import CorpusRepository

    ok, msg = check_connection()
    if not ok:
        console.print(f"[bold red]{msg}[/]")
        return

    session = get_session()
    repo = CorpusRepository(session)
    if args.question:
        deleted = repo.delete_cache(args.question)
        session.commit()
        if deleted:
            console.print(f"[green]Cache supprimé pour :[/] {args.question}")
        else:
            console.print(f"[yellow]Aucune entrée en cache pour :[/] {args.question}")
    else:
        count = repo.clear_cache()
        session.commit()
        console.print(f"[green]{count} entrée(s) de cache supprimée(s).[/]")
    session.close()


def cmd_multi_ask(args):
    """Question via multi-agent (constitution / élections / chiffres)."""
    if not _print_llm_banner():
        return

    from src.multi_agent import MultiAgentOrchestrator

    orch = MultiAgentOrchestrator()
    try:
        with console.status("[bold green]Analyse multi-agent..."):
            response = orch.ask(args.question, use_cache=not args.no_cache)
    except Exception as e:
        console.print(f"[bold red]Erreur :[/] {e}")
        sys.exit(1)
    finally:
        orch.close()

    cache_tag = " [dim](cache)[/]" if response.from_cache else ""
    console.print(f"[dim]Agent : {response.agent} | Thème : {response.topic}{cache_tag}[/]")
    console.print(Markdown(response.answer))


def cmd_multi_chat(args):
    """Chat interactif multi-agent France."""
    if not _print_llm_banner():
        return

    from src.db.engine import check_connection
    from src.multi_agent import MultiAgentOrchestrator

    ok, msg = check_connection()
    if not ok:
        console.print(f"[bold red]{msg}[/]")
        return

    orch = MultiAgentOrchestrator()
    stats = orch.get_stats()
    console.print(Panel(
        f"[bold]Multi-agent France[/] — {stats.get('total_chunks', 0)} chunks PostgreSQL\n"
        "Agents : constitution | élections | données chiffrées\n"
        "Tapez 'quit' pour quitter",
        title="DocIA France Civique",
    ))

    try:
        while True:
            try:
                question = console.input("\n[bold cyan]Vous :[/] ").strip()
            except (KeyboardInterrupt, EOFError):
                break
            if not question or question.lower() in ("quit", "exit", "q"):
                break
            with console.status("[bold green]Réflexion..."):
                response = orch.ask(question)
            tag = " [cache]" if response.from_cache else ""
            console.print(f"\n[dim][{response.agent}{tag}][/]")
            console.print(Markdown(response.answer))
    finally:
        orch.close()


def cmd_scrape(args):
    """Télécharge les sources officielles (Constitution, Élections)."""
    from src.scraping import scrape_all

    console.print("[bold blue]Scraping des sources officielles françaises...[/]")
    console.print("[dim]Légifrance, vie-publique, service-public, formation-civique, INSEE, Intérieur[/]")

    try:
        with console.status("[bold green]Téléchargement en cours (respect délai 1s/source)..."):
            result = scrape_all(
                category=args.category,
                discover_pdfs=not args.no_discover,
                include_datagouv=not args.no_datagouv,
                include_large_csv=not args.light,
                crawl_formation=not args.no_discover,
            )
    except Exception as e:
        console.print(f"[bold red]Erreur :[/] {e}")
        sys.exit(1)

    table = Table(title="Sources téléchargées", show_header=True)
    table.add_column("Catégorie", style="cyan")
    table.add_column("Document", style="green")
    for item in result.downloaded:
        table.add_row(item.category, item.title[:60])
    console.print(table)

    if result.failed:
        console.print(f"\n[yellow]{result.fail_count} échec(s) :[/]")
        for item in result.failed:
            console.print(f"  [red]X[/] {item.title}: {item.error}")

    console.print(f"\n[bold green]OK — {result.ok_count} fichier(s)[/]")
    if result.civic_crawled:
        console.print(f"[dim]Fiches formation-civique crawlées : {result.civic_crawled}[/]")
    if result.justice_crawled:
        console.print(f"[dim]Pages justice crawlées : {result.justice_crawled}[/]")
    console.print(f"Manifeste : {result.manifest_path}")

    if args.ingest:
        console.print("\n[bold blue]Ingestion PostgreSQL...[/]")
        if not _print_llm_banner():
            return
        from src.ingestion.pg_pipeline import ingest_directory
        from src.config import DOCUMENTS_DIR
        try:
            stats = ingest_directory(DOCUMENTS_DIR)
            console.print(
                f"[green]Ingestion : {stats['sources']} sources, "
                f"{stats['chunks']} chunks, {stats['tables']} tableaux[/]"
            )
        except Exception as e:
            console.print(f"[bold red]Ingestion échouée :[/] {e}")
            console.print("Lancez d'abord : docker compose up -d && python main.py pg-init")


def cmd_docker_install(args):
    """Guide / lance l'installation de Docker Desktop."""
    import subprocess

    console.print(Panel(
        "Docker Desktop est requis pour PostgreSQL (docker compose).\n\n"
        "1. Installation via winget (administrateur recommandé)\n"
        "2. Redémarrer la session Windows\n"
        "3. Lancer Docker Desktop depuis le menu Démarrer\n"
        "4. Activer WSL 2 si demandé\n"
        "5. docker compose up -d",
        title="Installation Docker",
    ))
    if args.launch:
        console.print("[bold blue]Lancement winget install Docker.DockerDesktop...[/]")
        proc = subprocess.run(
            [
                "winget", "install", "Docker.DockerDesktop",
                "--source", "winget",
                "--accept-package-agreements",
                "--accept-source-agreements",
            ],
            capture_output=False,
        )
        if proc.returncode == 0:
            console.print("[green]Installation lancée. Redémarrez Windows puis ouvrez Docker Desktop.[/]")
        else:
            console.print("[red]Échec winget. Exécutez en administrateur :[/]")
            console.print("  scripts\\install_docker.ps1")
    else:
        console.print("Pour lancer l'installation : python main.py docker-install --launch")


def main():
    parser = argparse.ArgumentParser(
        description="Agent IA RAG — Assistant documentaire intelligent",
    )
    subparsers = parser.add_subparsers(dest="command", help="Commandes disponibles")

    p_index = subparsers.add_parser("index", help="Indexer les documents")
    p_index.add_argument("--dir", help="Répertoire source (défaut: data/documents)")

    subparsers.add_parser("chat", help="Mode conversation interactif")

    p_ask = subparsers.add_parser("ask", help="Poser une question unique")
    p_ask.add_argument("question", help="Votre question")

    p_search = subparsers.add_parser("search", help="Rechercher un mot exact")
    p_search.add_argument("mot", help="Mot a chercher")

    subparsers.add_parser("stats", help="Afficher les statistiques")
    subparsers.add_parser("clear", help="Supprimer l'index vectoriel")

    subparsers.add_parser("pg-init", help="Initialiser PostgreSQL (tables)")
    p_pg_ingest = subparsers.add_parser("pg-ingest", help="Ingérer docs dans PostgreSQL")
    p_pg_ingest.add_argument("--dir", help="Répertoire source")
    p_pg_ingest.add_argument(
        "--justice-only", action="store_true",
        help="Uniquement les docs justice (lois, délits, crimes)",
    )
    subparsers.add_parser("pg-stats", help="Stats corpus PostgreSQL")
    p_pg_cache = subparsers.add_parser("pg-cache-clear", help="Vider le cache des réponses")
    p_pg_cache.add_argument("--question", help="Supprimer une seule question du cache")

    p_multi = subparsers.add_parser("multi-ask", help="Question multi-agent France")
    p_multi.add_argument("question", help="Votre question")
    p_multi.add_argument("--no-cache", action="store_true", help="Ignorer le cache")

    subparsers.add_parser("multi-chat", help="Chat multi-agent interactif")

    p_scrape = subparsers.add_parser("scrape", help="Télécharger sources officielles FR")
    p_scrape.add_argument(
        "--category", choices=["constitution", "elections", "justice", "test_civique"],
        help="Limiter à une catégorie (test_civique = examen civique / naturalisation)",
    )
    p_scrape.add_argument("--no-discover", action="store_true", help="Pas de PDF découverts ni crawler formation-civique")
    p_scrape.add_argument("--no-datagouv", action="store_true", help="Sans data.gouv.fr (résultats CSV)")
    p_scrape.add_argument("--light", action="store_true", help="Sans gros CSV agrégé")
    p_scrape.add_argument("--ingest", action="store_true", help="Ingérer dans PostgreSQL après")

    p_docker = subparsers.add_parser("docker-install", help="Installer Docker Desktop")
    p_docker.add_argument("--launch", action="store_true", help="Lancer winget install")

    args = parser.parse_args()

    commands = {
        "index": cmd_index,
        "chat": cmd_chat,
        "ask": cmd_ask,
        "search": cmd_search,
        "stats": cmd_stats,
        "clear": cmd_clear,
        "pg-init": cmd_pg_init,
        "pg-ingest": cmd_pg_ingest,
        "pg-stats": cmd_pg_stats,
        "pg-cache-clear": cmd_pg_cache_clear,
        "multi-ask": cmd_multi_ask,
        "multi-chat": cmd_multi_chat,
        "scrape": cmd_scrape,
        "docker-install": cmd_docker_install,
    }

    if args.command in commands:
        commands[args.command](args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
