"""Orchestrateur multi-agent — LangGraph + cache PostgreSQL."""

from src.db.engine import get_session
from src.db.repository import CorpusRepository
from src.langsmith_setup import build_run_config
from src.multi_agent.graph import build_france_graph, state_to_response
from src.multi_agent.types import MultiAgentResponse

__all__ = ["MultiAgentOrchestrator", "MultiAgentResponse"]


class MultiAgentOrchestrator:
    """Route la question via un graphe LangGraph vers l'agent spécialisé."""

    def __init__(self):
        self.session = get_session()
        self.repo = CorpusRepository(self.session)
        self._graph = build_france_graph(self.repo, self.session)

    def close(self):
        self.session.close()

    def get_stats(self) -> dict:
        return self.repo.get_stats()

    def ask(
        self,
        question: str,
        use_cache: bool = True,
        history: list[dict] | None = None,
        pinned_theme: str | None = None,
        *,
        trace_source: str = "streamlit",
    ) -> MultiAgentResponse:
        run_config = build_run_config(
            question,
            pinned_theme=pinned_theme,
            use_cache=use_cache,
            source=trace_source,
        )
        final_state = self._graph.invoke(
            {
                "question": question,
                "history": history or [],
                "pinned_theme": pinned_theme,
                "use_cache": use_cache,
            },
            run_config,
        )
        return state_to_response(final_state)
