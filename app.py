"""Interface web Streamlit pour l'agent RAG — design moderne."""

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

import src.startup  # noqa: F401

for _mod in [k for k in list(sys.modules) if k.startswith("src.") and k != "src.startup"]:
    del sys.modules[_mod]

import streamlit as st

from src.agent import RAGAgent
from src.config import DOCUMENTS_DIR, get_embedding_provider, get_llm_status, reload_env
from src.diagnostics import full_diagnostic, test_openai_connection
from src.errors import describe_error
from src.retrieval.vector_store import is_index_healthy
from src.ui.i18n import (
    get_france_suggestions,
    get_theme_cards,
    get_theme_followups,
    localized_prompt,
    t,
)
from src.ui.sidebar import render_nav_panel
from src.ui.civic_test_page import render_civic_test_page
from src.ui.theme import (
    hero_section,
    inject_styles,
    render_home_actions,
    render_theme_grid,
    section_title,
    stat_cards,
    status_pill,
)

_ENV_FILE = ROOT / ".env"

st.set_page_config(
    page_title="France Civique IA",
    page_icon="🇫🇷",
    layout="wide",
    initial_sidebar_state="expanded",
)

_VALID_PAGES = frozenset({"accueil", "chat", "france", "themes", "theme_explore", "test_civique", "faq", "admin"})


def _env_mtime() -> float:
    return _ENV_FILE.stat().st_mtime if _ENV_FILE.exists() else 0.0


def _index_mtime() -> float:
    reload_env()
    vs_dir = Path(os.getenv("VECTOR_STORE_DIR", ROOT / "data" / "vectorstore"))
    if not vs_dir.exists():
        return 0.0
    try:
        return max((p.stat().st_mtime for p in vs_dir.rglob("*") if p.is_file()), default=0.0)
    except OSError:
        return 0.0


def _agent_cache_key() -> str:
    return "|".join([
        _active_provider(), _active_model(), get_embedding_provider(),
        str(_env_mtime()), str(_index_mtime()),
        str(st.session_state.get("agent_nonce", 0)),
    ])


def _reload_agent():
    st.session_state.agent_nonce = st.session_state.get("agent_nonce", 0) + 1
    st.session_state.pop("agent", None)
    st.session_state.pop("agent_cache_key", None)


def _active_model() -> str:
    reload_env()
    if os.getenv("LLM_PROVIDER", "openai") == "ollama":
        return os.getenv("OLLAMA_MODEL", "llama3.2")
    return os.getenv("OPENAI_MODEL", "gpt-4o-mini")


def _active_provider() -> str:
    reload_env()
    return os.getenv("LLM_PROVIDER", "openai")


def _get_agent() -> RAGAgent:
    key = _agent_cache_key()
    if st.session_state.get("agent_cache_key") != key or "agent" not in st.session_state:
        st.session_state.agent = RAGAgent()
        st.session_state.agent_cache_key = key
    agent = st.session_state.agent
    if st.session_state.get("messages") and not agent.chat_history:
        agent.restore_conversation(st.session_state.messages)
    return agent


def _count_documents() -> int:
    if not DOCUMENTS_DIR.exists():
        return 0
    exts = {".pdf", ".txt", ".md", ".docx"}
    return sum(1 for f in DOCUMENTS_DIR.rglob("*") if f.is_file() and f.suffix.lower() in exts)


def _init_session():
    """Nouvelle session navigateur → page Accueil (hero + stats)."""
    defaults = {
        "agent_nonce": 0,
        "messages": [],
        "france_messages": [],
        "pending_index": False,
        "page": "accueil",
        "pending_question": None,
        "pending_france_question": None,
        "active_theme": None,
        "active_theme_title": None,
        "lang": "fr",
        "civic_tab_radio": "overview",
    }

    if "_session_ready" not in st.session_state:
        for k, v in defaults.items():
            st.session_state[k] = v
        st.session_state._session_ready = True
        st.session_state.page = "accueil"
    else:
        for k, v in defaults.items():
            if k not in st.session_state:
                st.session_state[k] = v

    if st.session_state.get("page") not in _VALID_PAGES:
        st.session_state.page = "accueil"

    for stale in ("menu_collapsed", "sidebar_visible"):
        st.session_state.pop(stale, None)


def _new_conversation(agent: RAGAgent):
    agent.clear_memory()
    st.session_state.messages = []
    st.session_state.france_messages = []
    st.session_state.pending_question = None
    st.session_state.pending_france_question = None
    st.session_state.active_theme = None
    st.session_state.active_theme_title = None
    if st.session_state.page not in ("chat", "france"):
        st.session_state.page = "chat"


def _sync_agent_memory(agent: RAGAgent):
    """Aligne la mémoire RAG sur les messages affichés dans le chat."""
    msgs = [
        m for m in st.session_state.get("messages", [])
        if m.get("role") in ("user", "assistant") and m.get("content")
    ]
    if msgs:
        agent.restore_conversation(msgs)
    elif agent.chat_history:
        agent.clear_memory()


def _chat_history_for_agent() -> list[dict]:
    """Historique à transmettre au multi-agent (sans le message en cours)."""
    return [
        m for m in st.session_state.get("messages", [])
        if m.get("role") in ("user", "assistant") and m.get("content")
    ]


def _render_nav(agent: RAGAgent, stats: dict, llm_status: dict):
    nav_page = st.session_state.page
    if nav_page == "theme_explore":
        nav_page = "themes"

    def on_nav(key: str):
        st.session_state.page = key
        st.rerun()

    def on_new_chat():
        _new_conversation(agent)
        st.rerun()

    render_nav_panel(
        active_page=nav_page,
        on_nav=on_nav,
        on_new_chat=on_new_chat,
        llm_ready=llm_status["ready"],
        llm_message=llm_status["message"],
    )


def _home_stat_items(agent_stats: dict) -> list[tuple[str, str]]:
    """Statistiques PostgreSQL si disponible, sinon index local."""
    lang = st.session_state.get("lang", "fr")
    elections_label = "ÉLECTIONS" if lang == "fr" else "ELECTIONS"
    try:
        from src.db import check_connection, get_session
        from src.db.repository import CorpusRepository

        ok, _ = check_connection()
        if ok:
            with get_session() as session:
                pg = CorpusRepository(session).get_stats()
            return [
                ("SOURCES", str(pg.get("total_sources", 0))),
                ("CHUNKS", str(pg.get("total_chunks", 0))),
                ("CONSTITUTION", str(pg.get("constitution_sources", 0))),
                (elections_label, str(pg.get("elections_sources", 0))),
            ]
    except Exception:
        pass
    model_label = "DOCUMENTS"
    return [
        ("CHUNKS", str(agent_stats.get("chunks_indexed", 0))),
        (model_label, str(_count_documents())),
        ("EMBEDDINGS", get_embedding_provider()[:10]),
        ("—", "—"),
    ]


def _page_accueil(stats: dict, llm_status: dict):
    with st.container(key="home_page"):
        hero_section(t("home_badge"), t("home_title"), t("home_text"))

        def _go_chat():
            st.session_state.page = "chat"
            st.rerun()

        def _go_themes():
            st.session_state.page = "themes"
            st.rerun()

        render_home_actions(t("home_btn_chat"), t("home_btn_themes"), _go_chat, _go_themes)

        section_title(t("home_stats_title"))
        home_stats = _home_stat_items(stats)
        stat_cards(home_stats)

        pg_chunks = next((int(v) for k, v in home_stats if k == "CHUNKS" and v.isdigit()), 0)
        if pg_chunks == 0 and stats.get("chunks_indexed", 0) == 0:
            st.warning(t("home_no_index"))


def _render_chat_messages(messages: list[dict], show_agent: bool = False):
    for msg in messages:
        with st.chat_message(msg["role"]):
            if show_agent and msg["role"] == "assistant":
                if msg.get("from_cache"):
                    st.caption(t("cache_caption"))
                if msg.get("agent"):
                    st.caption(t("agent_msg", agent=msg["agent"]))
            st.markdown(msg["content"])
            if msg.get("sources"):
                with st.expander(t("sources")):
                    for src in msg["sources"]:
                        st.markdown(f"**{src.get('file', '?')}**")
                        excerpt = src.get("excerpt") or src.get("type", "")
                        if excerpt:
                            st.caption(excerpt)


def _submit_chat_question(agent: RAGAgent, question: str):
    """Ajoute la question utilisateur et lance la recherche."""
    if not question.strip():
        return
    st.session_state.messages.append({"role": "user", "content": question})
    _run_query(agent, question)
    st.rerun()


def _render_theme_followups(agent: RAGAgent, theme_id: str):
    followups = get_theme_followups(theme_id)
    if not followups:
        return
    with st.expander(t("theme_continue_section"), expanded=not st.session_state.get("messages")):
        for i, item in enumerate(followups):
            col1, col2 = st.columns([4, 1])
            with col1:
                st.markdown(f"**{item['question']}** — {item['desc']}")
            with col2:
                if st.button(t("ask_btn"), key=f"theme_fu_{theme_id}_{i}", use_container_width=True):
                    _submit_chat_question(agent, item["question"])


def _page_theme_explore(agent: RAGAgent, llm_status: dict):
    theme_id = st.session_state.get("active_theme")
    theme_title = st.session_state.get("active_theme_title") or ""
    if not theme_id:
        st.session_state.page = "themes"
        st.rerun()
        return

    if not llm_status["ready"]:
        st.error(t("chat_llm_error"))
        return

    head_l, head_r = st.columns([5, 1])
    with head_l:
        st.markdown(f"### {t('theme_explore_title', theme=theme_title)}")
        st.caption(t("theme_change_hint"))
    with head_r:
        if st.button(t("theme_all_btn"), use_container_width=True):
            st.session_state.page = "themes"
            st.rerun()

    _render_chat_messages(st.session_state.messages)

    if st.session_state.get("pending_question"):
        q = st.session_state.pending_question
        st.session_state.pending_question = None
        if not st.session_state.messages or st.session_state.messages[-1].get("content") != q:
            st.session_state.messages.append({"role": "user", "content": q})
        with st.chat_message("user"):
            st.markdown(q)
        _run_query(agent, q)
        st.rerun()

    _render_theme_followups(agent, theme_id)

    placeholder = t("theme_chat_placeholder", theme=theme_title)
    if prompt := st.chat_input(placeholder):
        _submit_chat_question(agent, prompt)


def _page_chat(agent: RAGAgent, llm_status: dict):
    hero_section(t("chat_badge"), t("chat_title"), t("chat_text"))

    if not llm_status["ready"]:
        st.error(t("chat_llm_error"))
        return

    if st.session_state.get("active_theme_title"):
        st.markdown(t("theme_active", theme=st.session_state.active_theme_title))
        st.caption(t("theme_change_hint"))

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg.get("sources"):
                with st.expander(t("sources")):
                    for src in msg["sources"]:
                        st.markdown(f"**{src['file']}**")
                        st.caption(src.get("excerpt", ""))

    if st.session_state.get("pending_question"):
        q = st.session_state.pending_question
        st.session_state.pending_question = None
        if not st.session_state.messages or st.session_state.messages[-1].get("content") != q:
            st.session_state.messages.append({"role": "user", "content": q})
        with st.chat_message("user"):
            st.markdown(q)
        _run_query(agent, q)
        st.rerun()

    if prompt := st.chat_input(t("chat_placeholder")):
        _submit_chat_question(agent, prompt)


def _pg_ok_cached() -> bool:
    """Évite de retester PostgreSQL à chaque message (timeout 3s max)."""
    import time

    cache = st.session_state.get("_pg_ok_cache")
    now = time.time()
    if cache and now - cache["t"] < 60:
        return cache["ok"]
    from src.db.engine import check_connection

    ok, _ = check_connection()
    st.session_state["_pg_ok_cache"] = {"ok": ok, "t": now}
    return ok


def _run_query(agent: RAGAgent, prompt: str):
    prompt = localized_prompt(prompt)
    _sync_agent_memory(agent)
    history = _chat_history_for_agent()
    # Exclure le message courant (dernier ajouté) de l'historique transmis
    if history and history[-1].get("role") == "user" and history[-1].get("content") == prompt:
        history = history[:-1]

    if _pg_ok_cached():
        if _run_france_query(prompt, history=history):
            _sync_agent_memory(agent)
            return

    with st.chat_message("assistant"):
        with st.spinner(t("chat_analyzing")):
            try:
                response = agent.query(prompt)
            except Exception as e:
                err = t("error", msg=e)
                st.error(err)
                with st.expander(t("tech_detail")):
                    st.code(describe_error(e))
                st.session_state.messages.append({"role": "assistant", "content": err, "sources": []})
                return
        st.markdown(response.answer)
        if response.sources:
            with st.expander(t("sources")):
                for src in response.sources:
                    st.markdown(f"**{src['file']}**")
                    st.caption(src["excerpt"])
    st.session_state.messages.append({
        "role": "assistant",
        "content": response.answer,
        "sources": response.sources,
    })
    _sync_agent_memory(agent)


def _pg_stats() -> dict:
    from src.db.engine import get_session
    from src.db.repository import CorpusRepository

    session = get_session()
    try:
        return CorpusRepository(session).get_stats()
    finally:
        session.close()


def _run_france_query(prompt: str, history: list[dict] | None = None) -> bool:
    """Exécute une requête multi-agent. Retourne True si une réponse a été produite."""
    from src.db.engine import check_connection
    from src.multi_agent import MultiAgentOrchestrator

    prompt = localized_prompt(prompt)
    ok, msg = check_connection()
    if not ok:
        st.error(t("pg_unavailable", msg=msg))
        st.info(t("pg_hint"))
        return False

    orch = MultiAgentOrchestrator()
    answer_text = ""
    response = None
    pinned = st.session_state.get("active_theme")
    try:
        with st.chat_message("assistant"):
            with st.spinner(t("routing")):
                try:
                    response = orch.ask(
                        prompt,
                        history=history or [],
                        pinned_theme=pinned,
                    )
                except Exception as e:
                    st.session_state.pop("orchestrator", None)
                    err = t("error", msg=e)
                    st.error(err)
                    with st.expander(t("tech_detail")):
                        st.code(describe_error(e))
                    answer_text = err
                    entry = {"role": "assistant", "content": err, "agent": "error", "sources": []}
                    st.session_state.france_messages.append(entry)
                    st.session_state.messages.append({"role": "assistant", "content": err, "sources": []})
                    return True
            if response.from_cache:
                st.caption(t("cache_caption"))
            st.caption(t("agent_caption", agent=response.agent, topic=response.topic))
            st.markdown(response.answer)
            answer_text = response.answer
            if response.sources:
                with st.expander(t("sources")):
                    for src in response.sources:
                        st.markdown(f"**{src.get('file', '?')}** ({src.get('type', 'doc')})")
    finally:
        orch.close()

    entry = {
        "role": "assistant",
        "content": answer_text,
        "agent": response.agent,
        "from_cache": response.from_cache,
        "sources": response.sources,
    }
    st.session_state.france_messages.append(entry)
    st.session_state.messages.append({
        "role": "assistant",
        "content": answer_text,
        "sources": [
            {"file": s.get("file", "?"), "excerpt": s.get("type", "doc")}
            for s in (response.sources or [])
        ],
    })
    return True


def _page_france(llm_status: dict):
    hero_section(t("france_badge"), t("france_title"), t("france_text"))

    if not llm_status["ready"]:
        st.error(t("chat_llm_error"))
        return

    from src.db.engine import check_connection

    ok, pg_msg = check_connection()
    if ok:
        status_pill(t("pg_ok"))
        stats = _pg_stats()
        elections_label = "ÉLECTIONS" if st.session_state.get("lang", "fr") == "fr" else "ELECTIONS"
        justice_label = "JUSTICE" if st.session_state.get("lang", "fr") == "fr" else "JUSTICE"
        stat_cards([
            ("SOURCES", str(stats.get("total_sources", 0))),
            ("CHUNKS", str(stats.get("total_chunks", 0))),
            ("CONSTITUTION", str(stats.get("constitution_sources", 0))),
            (elections_label, str(stats.get("elections_sources", 0))),
            (justice_label, str(stats.get("justice_sources", 0))),
        ])
        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric(t("facts"), stats.get("total_facts", 0))
        with c2:
            st.metric(t("tables"), stats.get("total_tables", 0))
        with c3:
            st.metric(t("cache_hits"), stats.get("cached_queries", 0))
    else:
        status_pill(t("pg_ko", msg=pg_msg), ok=False)
        st.code("docker compose up -d\npython main.py pg-init\npython main.py pg-ingest")

    with st.expander(t("pgadmin_title")):
        note = (
            "Ne pas utiliser le serveur Localhost port 5432 (PostgreSQL Windows)."
            if st.session_state.get("lang", "fr") == "fr"
            else "Do not use Localhost server port 5432 (Windows PostgreSQL)."
        )
        st.markdown(
            f"""
            <div class="info-card">
            <strong>France Civique IA — Docker</strong><br><br>
            Host: <code>127.0.0.1</code> · Port: <code>5433</code><br>
            Database: <code>docia_fr</code> · User: <code>docia</code><br>
            Password: <code>docia_secret</code><br><br>
            <em>{note}</em>
            </div>
            """,
            unsafe_allow_html=True,
        )

    section_title(t("france_section"))

    if st.session_state.get("pending_france_question"):
        q = st.session_state.pending_france_question
        st.session_state.pending_france_question = None
        st.session_state.france_messages.append({"role": "user", "content": q})
        with st.chat_message("user"):
            st.markdown(q)
        _run_france_query(q)
        return

    for msg in st.session_state.france_messages:
        with st.chat_message(msg["role"]):
            if msg["role"] == "assistant":
                if msg.get("from_cache"):
                    st.caption(t("cache_caption"))
                if msg.get("agent"):
                    st.caption(t("agent_msg", agent=msg["agent"]))
            st.markdown(msg["content"])
            if msg.get("sources"):
                with st.expander(t("sources")):
                    for src in msg["sources"]:
                        st.markdown(f"**{src.get('file', '?')}** ({src.get('type', 'doc')})")

    if prompt := st.chat_input(t("france_placeholder")):
        st.session_state.france_messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        _run_france_query(prompt)

    with st.expander(t("suggestions")):
        for title, question, desc in get_france_suggestions():
            col1, col2 = st.columns([4, 1])
            with col1:
                st.markdown(f"**{title}** — {desc}")
            with col2:
                if st.button(t("ask_btn"), key=f"fr_{title}", use_container_width=True):
                    st.session_state.pending_france_question = question
                    st.rerun()


def _page_themes():
    hero_section(
        f"📋 {t('themes_section')}",
        t("themes_hero_title"),
        t("themes_hero_text"),
    )

    if st.session_state.get("active_theme") and st.session_state.get("messages"):
        theme_title = st.session_state.get("active_theme_title", "")
        c1, c2 = st.columns([3, 1])
        with c1:
            st.info(t("theme_active", theme=theme_title))
        with c2:
            if st.button(t("theme_resume_btn"), use_container_width=True, type="primary"):
                st.session_state.page = "theme_explore"
                st.rerun()

    def on_explore(question: str, theme_id: str, theme_title: str):
        if st.session_state.get("active_theme") != theme_id:
            st.session_state.messages = []
            st.session_state.france_messages = []
        st.session_state.active_theme = theme_id
        st.session_state.active_theme_title = theme_title
        st.session_state.page = "theme_explore"
        st.session_state.pending_question = question
        st.rerun()

    render_theme_grid(get_theme_cards(), t("explore_btn"), on_explore)


def _page_faq():
    hero_section(
        "❓ AIDE",
        "Questions fréquentes",
        "Tout ce qu'il faut savoir pour utiliser DocIA efficacement.",
    )

    faqs = [
        ("Comment indexer mes documents ?", 
         "Allez dans **Configuration** → uploadez vos fichiers → **Enregistrer** → **Indexer les documents**."),
        ("Quels formats sont supportés ?", 
         "PDF, TXT, Markdown (.md) et Word (.docx)."),
        ("L'agent se souvient-il de la conversation ?", 
         "Oui. Vous pouvez enchaîner : « article 2 » puis « et l'article 3 ? »."),
        ("Pourquoi « Connexion OpenAI échouée » ?", 
         "Lancez `python run_app.py`, cliquez **Tester connexion OpenAI**, puis **Recharger l'agent**. Voir `docs/DEPANNAGE.md`."),
        ("Puis-je utiliser Ollama gratuitement ?", 
         "Oui. Dans `.env` : `LLM_PROVIDER=ollama` et `EMBEDDING_PROVIDER=tfidf`."),
    ]
    for q, a in faqs:
        with st.expander(q):
            st.markdown(a)


def _page_admin(agent: RAGAgent, stats: dict, index_ok: bool):
    hero_section(
        "⚙️ CONFIGURATION",
        "Gérer l'agent et les documents",
        "Testez la connexion, indexez vos fichiers et surveillez l'état du système.",
    )

    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("Tester OpenAI", use_container_width=True):
            ok, msg = test_openai_connection()
            st.success(msg) if ok else st.error(msg)
            if not ok:
                st.code(msg)
    with c2:
        if st.button("Diagnostic complet", use_container_width=True):
            st.code("\n".join(full_diagnostic()))
    with c3:
        if st.button("Recharger l'agent", use_container_width=True):
            _reload_agent()
            st.rerun()

    st.metric("Chunks indexés", stats["chunks_indexed"])
    if not index_ok and stats["chunks_indexed"] == 0:
        st.error("Index absent ou corrompu — réindexez ci-dessous.")

    st.subheader("Documents")
    uploaded = st.file_uploader(
        "Ajouter des fichiers", type=["pdf", "txt", "md", "docx"], accept_multiple_files=True
    )
    if uploaded and st.button("Enregistrer les fichiers"):
        DOCUMENTS_DIR.mkdir(parents=True, exist_ok=True)
        for f in uploaded:
            (DOCUMENTS_DIR / f.name).write_bytes(f.getvalue())
        st.success(f"{len(uploaded)} fichier(s) enregistré(s)")
        st.session_state.pending_index = True

    col_a, col_b, col_c = st.columns(3)
    with col_a:
        if st.button("Indexer les documents", type="primary", use_container_width=True):
            with st.spinner("Indexation..."):
                result = agent.index_documents_detailed()
                _reload_agent()
            st.success(f"{result.chunks} chunks indexés") if result.chunks else st.warning("Aucun document")
            st.rerun()
    with col_b:
        if st.button("Supprimer l'index", use_container_width=True):
            agent.clear_index()
            _reload_agent()
            st.rerun()
    with col_c:
        if st.button("Effacer la conversation", use_container_width=True):
            agent.clear_memory()
            st.session_state.messages = []
            st.rerun()

    st.divider()
    st.subheader("Sources officielles — Web scraping")
    st.caption("Télécharge Constitution, élections, justice, test civique depuis les sites gouvernementaux.")
    col_sc1, col_sc2, col_sc3 = st.columns(3)
    with col_sc1:
        if st.button("Télécharger toutes les sources", use_container_width=True):
            from src.scraping import scrape_all
            with st.spinner("Scraping (≈15 sources, 1 req/s)..."):
                try:
                    sr = scrape_all()
                    st.success(f"{sr.ok_count} fichier(s) — {sr.fail_count} échec(s)")
                    if sr.failed:
                        with st.expander("Échecs"):
                            for f in sr.failed:
                                st.caption(f"{f.title}: {f.error}")
                except Exception as e:
                    st.error(str(e))
            st.rerun()
    with col_sc2:
        cat = st.selectbox("Catégorie", ["Toutes", "constitution", "elections", "justice", "test_civique"], label_visibility="collapsed")
    with col_sc3:
        if st.button("Télécharger catégorie", use_container_width=True):
            from src.scraping import scrape_all
            c = None if cat == "Toutes" else cat
            with st.spinner("Scraping..."):
                try:
                    sr = scrape_all(category=c)
                    st.success(f"{sr.ok_count} fichier(s)")
                except Exception as e:
                    st.error(str(e))
            st.rerun()

    st.divider()
    st.subheader("PostgreSQL — Multi-agent France")
    from src.db.engine import check_connection

    pg_ok, pg_msg = check_connection()
    st.caption(f"{'🟢' if pg_ok else '🔴'} {pg_msg}")
    col_pg1, col_pg2 = st.columns(2)
    with col_pg1:
        if st.button("Initialiser PostgreSQL", use_container_width=True):
            from src.db.engine import init_db
            init_db()
            st.success("Tables créées")
            st.rerun()
    with col_pg2:
        if st.button("Ingérer dans PostgreSQL", type="primary", use_container_width=True):
            from src.ingestion.pg_pipeline import ingest_directory
            with st.spinner("Ingestion (texte, tableaux, chiffres)..."):
                try:
                    result = ingest_directory()
                except Exception as e:
                    st.error(str(e))
                else:
                    st.success(
                        f"{result['sources']} sources, {result['chunks']} chunks, "
                        f"{result['tables']} tableaux, {result['facts']} faits"
                    )
                    st.session_state.pop("orchestrator", None)
                    st.rerun()


def main():
    reload_env()
    _init_session()
    inject_styles()

    agent = _get_agent()
    stats = agent.get_stats()
    llm_status = get_llm_status()
    index_ok = is_index_healthy()

    with st.sidebar:
        _render_nav(agent, stats, llm_status)

    pages = {
        "accueil": lambda: _page_accueil(stats, llm_status),
        "chat": lambda: _page_chat(agent, llm_status),
        "france": lambda: _page_france(llm_status),
        "themes": _page_themes,
        "theme_explore": lambda: _page_theme_explore(agent, llm_status),
        "test_civique": render_civic_test_page,
        "faq": _page_faq,
        "admin": lambda: _page_admin(agent, stats, index_ok),
    }
    current = st.session_state.get("page", "accueil")
    if current not in pages:
        current = "accueil"
        st.session_state.page = "accueil"
    pages[current]()


if __name__ == "__main__":
    main()
