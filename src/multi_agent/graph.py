"""Workflow LangGraph — routage multi-agent France Civique."""

from __future__ import annotations

from typing import Any, TypedDict

from langgraph.graph import END, START, StateGraph

from src.db.repository import CorpusRepository
from src.ingestion.classifier import enrich_search_query
from src.multi_agent.agents import AGENTS, AgentResult
from src.multi_agent.conversation import (
    enrich_with_history,
    format_history,
    is_follow_up,
    resolve_topic,
)
from src.multi_agent.types import MultiAgentResponse, is_stale_cache_answer


class FranceGraphState(TypedDict, total=False):
    question: str
    history: list[dict]
    pinned_theme: str | None
    use_cache: bool
    has_history: bool
    topic: str
    search_q: str
    history_text: str | None
    answer: str
    agent: str
    sources: list[dict]
    from_cache: bool
    elapsed_hint: str
    done: bool


def build_france_graph(repo: CorpusRepository, session) -> Any:
    """Construit le graphe : cache → routage → agent → sauvegarde cache."""

    def validate(state: FranceGraphState) -> FranceGraphState:
        question = (state.get("question") or "").strip()
        if not question:
            return {
                "answer": "Veuillez poser une question.",
                "agent": "none",
                "topic": "none",
                "sources": [],
                "from_cache": False,
                "done": True,
            }
        history = state.get("history") or []
        use_cache = state.get("use_cache", True)
        if history or is_follow_up(question, history):
            use_cache = False
        return {
            "question": question,
            "history": history,
            "use_cache": use_cache,
            "has_history": bool(history),
            "from_cache": False,
            "sources": [],
            "done": False,
        }

    def check_cache(state: FranceGraphState) -> FranceGraphState:
        if state.get("done") or not state.get("use_cache", True):
            return {}
        cached = repo.get_cache(state["question"])
        if cached and not is_stale_cache_answer(cached.answer):
            repo.bump_cache_hit(cached)
            session.commit()
            return {
                "answer": cached.answer,
                "agent": cached.agent_used or "cache",
                "topic": "cached",
                "sources": cached.sources if isinstance(cached.sources, list) else [],
                "from_cache": True,
                "elapsed_hint": "instantané (cache)",
                "done": True,
            }
        if cached and is_stale_cache_answer(cached.answer):
            repo.delete_cache(state["question"])
        return {}

    def route_topic(state: FranceGraphState) -> FranceGraphState:
        if state.get("done"):
            return {}
        question = state["question"]
        history = state.get("history") or []
        topic = resolve_topic(question, history, state.get("pinned_theme"))
        search_q = enrich_search_query(question, topic)
        if state.get("has_history"):
            search_q = enrich_with_history(search_q, history)
        history_text = format_history(history) if history else None
        return {
            "topic": topic,
            "search_q": search_q,
            "history_text": history_text,
        }

    def run_agent(state: FranceGraphState) -> FranceGraphState:
        if state.get("done"):
            return {}
        topic = state.get("topic", "general")
        agent_cls = AGENTS.get(topic, AGENTS["general"])
        agent = agent_cls(session, repo)
        try:
            result: AgentResult = agent.run(
                state["search_q"],
                display_question=state["question"],
                conversation_context=state.get("history_text"),
                history=state.get("history"),
            )
        except Exception:
            session.rollback()
            raise
        return {
            "answer": result.answer,
            "agent": result.agent,
            "sources": result.sources,
            "from_cache": False,
        }

    def save_cache(state: FranceGraphState) -> FranceGraphState:
        if state.get("done") or not state.get("use_cache", True):
            return {"done": True}
        answer = state.get("answer", "")
        if (
            answer
            and "non trouvé" not in answer.lower()[:80]
            and not is_stale_cache_answer(answer)
        ):
            repo.set_cache(
                state["question"],
                answer,
                state.get("agent", "general"),
                state.get("sources") or [],
            )
            session.commit()
        return {"done": True}

    def after_validate(state: FranceGraphState) -> str:
        return "finish" if state.get("done") else "cache"

    def after_cache(state: FranceGraphState) -> str:
        return "finish" if state.get("done") else "route"

    graph = StateGraph(FranceGraphState)
    graph.add_node("validate", validate)
    graph.add_node("check_cache", check_cache)
    graph.add_node("route_topic", route_topic)
    graph.add_node("run_agent", run_agent)
    graph.add_node("save_cache", save_cache)

    graph.add_edge(START, "validate")
    graph.add_conditional_edges(
        "validate", after_validate, {"finish": END, "cache": "check_cache"}
    )
    graph.add_conditional_edges(
        "check_cache", after_cache, {"finish": END, "route": "route_topic"}
    )
    graph.add_edge("route_topic", "run_agent")
    graph.add_edge("run_agent", "save_cache")
    graph.add_edge("save_cache", END)

    return graph.compile()


def get_graph_mermaid() -> str:
    """Schéma Mermaid du workflow (debug / admin)."""
    return """
flowchart LR
    START --> validate
    validate -->|vide| END
    validate --> check_cache
    check_cache -->|hit| END
    check_cache --> route_topic
    route_topic --> run_agent
    run_agent --> save_cache
    save_cache --> END
""".strip()


def state_to_response(state: FranceGraphState) -> MultiAgentResponse:
    return MultiAgentResponse(
        answer=state.get("answer", ""),
        agent=state.get("agent", "general"),
        topic=state.get("topic", "general"),
        sources=state.get("sources") or [],
        from_cache=bool(state.get("from_cache")),
        elapsed_hint=state.get("elapsed_hint", ""),
    )
