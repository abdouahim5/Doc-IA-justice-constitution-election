"""Orchestrateur multi-agent — routage, cache, réponse instantanée."""

from dataclasses import dataclass, field

from src.db.engine import get_session
from src.db.repository import CorpusRepository
from src.ingestion.classifier import classify_question, enrich_search_query
from src.multi_agent.agents import AGENTS, AgentResult
from src.multi_agent.conversation import (
    enrich_with_history,
    format_history,
    is_follow_up,
    resolve_topic,
)

_EXTRACTIVE_PREFIX = "D'après les sources officielles indexées"


def _is_stale_cache_answer(answer: str) -> bool:
    """Ignore les anciennes réponses extractives incorrectes."""
    return answer.strip().startswith(_EXTRACTIVE_PREFIX)


@dataclass
class MultiAgentResponse:
    answer: str
    agent: str
    topic: str
    sources: list[dict] = field(default_factory=list)
    from_cache: bool = False
    elapsed_hint: str = ""


class MultiAgentOrchestrator:
    """Route la question vers l'agent spécialisé et utilise le cache PostgreSQL."""

    def __init__(self):
        self.session = get_session()
        self.repo = CorpusRepository(self.session)

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
        question = question.strip()
        if not question:
            return MultiAgentResponse(
                answer="Veuillez poser une question.",
                agent="none", topic="none",
            )

        history = history or []
        has_history = bool(history)
        if has_history or is_follow_up(question, history):
            use_cache = False

        if use_cache:
            cached = self.repo.get_cache(question)
            if cached and not _is_stale_cache_answer(cached.answer):
                self.repo.bump_cache_hit(cached)
                self.session.commit()
                return MultiAgentResponse(
                    answer=cached.answer,
                    agent=cached.agent_used or "cache",
                    topic="cached",
                    sources=cached.sources if isinstance(cached.sources, list) else [],
                    from_cache=True,
                    elapsed_hint="instantané (cache)",
                )
            if cached and _is_stale_cache_answer(cached.answer):
                self.repo.delete_cache(question)

        topic = resolve_topic(question, history, pinned_theme)
        agent_cls = AGENTS.get(topic, AGENTS["general"])
        agent = agent_cls(self.session, self.repo)
        search_q = enrich_search_query(question, topic)
        if has_history:
            search_q = enrich_with_history(search_q, history)
        history_text = format_history(history) if has_history else None
        try:
            result: AgentResult = agent.run(
                search_q,
                display_question=question,
                conversation_context=history_text,
            )
        except Exception:
            self.session.rollback()
            raise

        if (
            use_cache
            and result.answer
            and "non trouvé" not in result.answer.lower()[:80]
            and not _is_stale_cache_answer(result.answer)
        ):
            self.repo.set_cache(question, result.answer, result.agent, result.sources)
            self.session.commit()

        return MultiAgentResponse(
            answer=result.answer,
            agent=result.agent,
            topic=topic,
            sources=result.sources,
            from_cache=False,
        )
