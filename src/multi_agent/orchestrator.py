"""Orchestrateur multi-agent — LangGraph + cache PostgreSQL."""

from src.db.engine import get_session
from src.db.repository import CorpusRepository
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
    ) -> MultiAgentResponse:
        final_state = self._graph.invoke({
            "question": question,
            "history": history or [],
            "pinned_theme": pinned_theme,
            "use_cache": use_cache,
        })
        return state_to_response(final_state)
