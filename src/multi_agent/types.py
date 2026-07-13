"""Types partagés multi-agent."""

from dataclasses import dataclass, field

_EXTRACTIVE_PREFIX = "D'après les sources officielles indexées"


def is_stale_cache_answer(answer: str) -> bool:
    return answer.strip().startswith(_EXTRACTIVE_PREFIX)


@dataclass
class MultiAgentResponse:
    answer: str
    agent: str
    topic: str
    sources: list[dict] = field(default_factory=list)
    from_cache: bool = False
    elapsed_hint: str = ""
