"""Agents spécialisés — Constitution, Élections, Données chiffrées."""

from dataclasses import dataclass, field
from functools import lru_cache

from langchain_core.prompts import ChatPromptTemplate
from sqlalchemy.orm import Session

from src.config import get_multi_agent_settings
from src.db.repository import CorpusRepository
from src.llm import get_llm
from src.retrieval.hybrid_retriever import _extract_article_numbers, text_has_article


@dataclass
class AgentResult:
    answer: str
    agent: str
    sources: list[dict] = field(default_factory=list)
    from_cache: bool = False


@lru_cache(maxsize=1)
def _shared_llm():
    return get_llm()


_EMBED_CACHE: dict[str, list[float]] = {}
_EMBED_CACHE_MAX = 128


def _cached_embed(text: str, embedder) -> list[float]:
    key = text.strip()[:256]
    if key in _EMBED_CACHE:
        return _EMBED_CACHE[key]
    vec = embedder.embed_query(text)
    if len(_EMBED_CACHE) >= _EMBED_CACHE_MAX:
        _EMBED_CACHE.pop(next(iter(_EMBED_CACHE)))
    _EMBED_CACHE[key] = vec
    return vec


SYSTEM_CONSTITUTION = """Tu es un expert en droit constitutionnel français.
Réponds UNIQUEMENT à partir des extraits fournis.
Cite [nom_fichier] et le numéro d'article si pertinent.
Si l'information manque : "Non trouvé dans les sources indexées."
Rédige une réponse en phrases complètes et claires (pas d'extraits bruts)."""

SYSTEM_CONSTITUTION_ARTICLE = """Tu es un expert en droit constitutionnel français.

La question porte sur un ARTICLE précis de la Constitution. Les extraits contiennent cet article.
Recopie fidèlement le texte de l'article demandé, puis résume-le en français clair si utile.
Cite la source : [nom_fichier].
N'invente rien. Si l'article n'est pas dans les extraits, dis :
"Non trouvé dans les sources indexées."
"""

SYSTEM_ELECTIONS = """Tu es un expert en élections et vie démocratique en France.
Réponds UNIQUEMENT à partir des extraits, tableaux et chiffres fournis.
Cite [nom_fichier]. Mentionne les pourcentages et dates exacts des sources.
Si l'information manque : "Non trouvé dans les sources indexées."
Réponds en français."""

SYSTEM_DATA = """Tu es un analyste de données électorales et statistiques françaises.
Utilise UNIQUEMENT les faits chiffrés et tableaux fournis.
Présente les chiffres clairement (tableau ou liste). Cite la source.
Si absent : "Chiffre non trouvé dans les sources indexées."""

SYSTEM_GENERAL = """Tu es un assistant documentaire sur la France (constitution, élections, justice).
Réponds uniquement à partir des sources fournies. Cite [nom_fichier].
Rédige une réponse en phrases complètes (4 à 8 phrases), claire et structurée.
Ne recopie pas d'extraits bruts : synthétise en français."""

SYSTEM_JUSTICE = """Tu es un expert en droit français : lois, codes, procédure et jurisprudence.
Réponds UNIQUEMENT à partir des extraits fournis (Légifrance, cours, service-public).
Cite [nom_fichier]. Précise le texte, l'article ou la juridiction quand c'est dans les sources.
Si l'information manque : "Non trouvé dans les sources indexées."
Réponds en français, clair et structuré."""

SYSTEM_TEST_CIVIQUE = """Tu es un formateur pour l'examen civique français (naturalisation, titre de séjour).
Réponds UNIQUEMENT à partir des extraits fournis (formation civique, livret du citoyen, service-public).
Cite [nom_fichier]. Structure ta réponse clairement.
Si l'information manque : "Non trouvé dans les sources indexées."
Réponds en français."""


def _score_float(val) -> float:
    try:
        return float(val)
    except (TypeError, ValueError):
        return 0.0


def _unpack_hit(item) -> tuple[str, float, str]:
    """Retourne (contenu, score, fichier) — formats repo ou déjà normalisés."""
    if isinstance(item, tuple) and len(item) == 3:
        first, second, third = item[0], item[1], item[2]
        if hasattr(first, "content"):
            return first.content, _score_float(second), str(third)
        if isinstance(first, str):
            if isinstance(second, (int, float)):
                return first, float(second), str(third)
            return first, _score_float(third), str(second)
    return str(item[0]), _score_float(item[1]), str(item[2])


def _format_chunks(hits: list, max_chars: int = 800) -> str:
    parts = []
    for item in hits:
        content, _score, fname = _unpack_hit(item)
        parts.append(f"=== [{fname}] ===\n{content[:max_chars]}")
    return "\n\n".join(parts) if parts else "(aucun extrait)"


def _format_facts(facts) -> str:
    if not facts:
        return "(aucun fait chiffré)"
    lines = []
    for f in facts:
        ctx = f.context[:100] if f.context else ""
        lines.append(f"- {f.fact_key}: {f.fact_value} [{ctx}]")
    return "\n".join(lines[:15])


def _format_tables(tables) -> str:
    if not tables:
        return "(aucun tableau)"
    parts = []
    for t in tables:
        parts.append(f"=== Tableau p.{t.page_number} ===\n{t.raw_text[:800]}")
    return "\n\n".join(parts)


def _is_short_query(question: str) -> bool:
    return len(question.strip().split()) <= 4


def _fold_text(text: str) -> str:
    import unicodedata
    n = unicodedata.normalize("NFD", text.lower())
    return "".join(c for c in n if unicodedata.category(c) != "Mn")


def _is_president_eligibility_question(question: str) -> bool:
    q = _fold_text(question)
    return any(k in q for k in ("president", "presidentielle")) and any(
        k in q for k in ("condition", "eligib", "etre", "candidat", "devenir", "pour", "peut")
    )


def _needs_synthesis(question: str) -> bool:
    """Questions qui exigent une réponse rédigée, pas des extraits."""
    if _is_article_query(question) or _is_president_eligibility_question(question):
        return True
    q = _fold_text(question)
    markers = (
        "condition", "comment", "pourquoi", "quelles", "quels", "que dit",
        "expliquer", "definir", "c est quoi", "difference", "role", "pouvoir",
        "pour etre", "peut on", "doit on", "qu est ce",
    )
    return any(m in q for m in markers)


def _best_excerpt(text: str, terms: list[str], max_chars: int = 420) -> str:
    low = text.lower()
    for term in terms:
        t = term.lower()
        idx = low.find(t)
        if idx >= 0:
            start = max(0, idx - 100)
            snippet = text[start : start + max_chars].strip()
            return snippet + ("…" if start + max_chars < len(text) else "")
    snippet = text[:max_chars].strip()
    return snippet + ("…" if len(text) > max_chars else "")


def _is_article_query(question: str) -> bool:
    return bool(_extract_article_numbers(question))


def _article_patterns(nums: list[int]) -> list[str]:
    patterns: list[str] = []
    for n in nums:
        patterns.extend([
            f"%ARTICLE {n}.%",
            f"%Article {n}.%",
            f"%article {n}.%",
            f"%### ARTICLE {n}.%",
            f"%ARTICLE {n} %",
            f"%Art. {n}.%",
        ])
    return list(dict.fromkeys(patterns))


def _normalize_hits(hits: list) -> list[tuple[str, float, str]]:
    return [_unpack_hit(item) for item in hits]


def _filter_article_chunks(
    chunks: list, nums: list[int],
) -> list[tuple[str, float, str]]:
    return [
        item for item in _normalize_hits(chunks)
        if any(text_has_article(item[0], n) for n in nums)
    ]


def _extractive_answer(chunks: list, question: str, max_chars: int) -> str | None:
    """Réponse directe depuis les extraits — sans appel LLM."""
    if not chunks:
        return None
    terms = [w.strip("?.!,;:") for w in question.split() if len(w.strip("?.!,;:")) >= 3]
    if not terms:
        terms = [w.strip("?.!,;:") for w in question.split() if len(w.strip("?.!,;:")) >= 2]
    parts = ["D'après les sources officielles indexées :\n"]
    for item in chunks[:3]:
        content, _score, fname = _unpack_hit(item)
        parts.append(f"**[{fname}]**\n{_best_excerpt(content, terms, max_chars)}")
    return "\n\n".join(parts)


def _merge_text_hits(
    text_hits: list,
    pattern_hits: list,
    vector_hits: list | None = None,
    max_chunks: int = 5,
) -> list:
    combined: list = []
    for group in (vector_hits or [], text_hits, pattern_hits):
        for item in group:
            if hasattr(item[0], "content"):
                combined.append(item)
            else:
                combined.append(_unpack_hit(item))
    out: list = []
    seen_files: set[str] = set()
    for item in combined:
        _content, _score, fname = _unpack_hit(item)
        if fname not in seen_files:
            out.append(item)
            seen_files.add(fname)
    return out[:max_chunks]


def _text_only_retrieve(
    repo: CorpusRepository,
    question: str,
    category: str | None,
    cfg: dict,
    extra_patterns: list[str] | None = None,
) -> tuple[list, list, list]:
    """Recherche ILIKE uniquement — pas d'appel API embedding."""
    patterns = list(extra_patterns or [])
    for w in question.split():
        w = w.strip("?.!,;:")
        if len(w) >= 3:
            patterns.append(f"%{w}%")
    patterns = list(dict.fromkeys(patterns))[:6]

    text_hits = repo.search_text(question, category, cfg["text_limit"])
    pattern_hits = (
        repo.search_chunks_patterns(patterns, category, 3) if patterns else []
    )

    chunks = _merge_text_hits(text_hits, pattern_hits, max_chunks=cfg["max_chunks"])
    return chunks, [], []


class BaseSpecialistAgent:
    name: str = "base"
    category: str | None = None
    system_prompt: str = SYSTEM_GENERAL

    def __init__(self, session: Session, repo: CorpusRepository):
        self.repo = repo
        self.llm = _shared_llm()
        self.embedder = None

    def _embed(self, text: str) -> list[float]:
        if self.embedder is None:
            from src.retrieval.vector_store import _get_embeddings
            self.embedder = _get_embeddings()
        return _cached_embed(text, self.embedder)

    def retrieve(
        self, question: str, display_question: str | None = None,
    ) -> tuple[list, list, list]:
        cfg = get_multi_agent_settings()
        intent_q = display_question or question
        article_nums = _extract_article_numbers(question)
        if article_nums:
            return self._retrieve_article(question, article_nums, cfg)

        if cfg["text_only"]:
            return _text_only_retrieve(self.repo, question, self.category, cfg)

        emb = self._embed(question)
        vector_hits = self.repo.search_vector(
            emb, category=self.category, limit=cfg["vector_limit"]
        )
        text_hits = self.repo.search_text(
            question, category=self.category, limit=cfg["text_limit"]
        )

        chunks = _merge_text_hits(text_hits, [], vector_hits, cfg["max_chunks"])
        return chunks, [], []

    def _retrieve_article(
        self, question: str, article_nums: list[int], cfg: dict
    ) -> tuple[list, list, list]:
        """Recherche ciblée sur un numéro d'article (toujours avec vecteurs)."""
        patterns = _article_patterns(article_nums)
        search_q = f"{' '.join(f'article {n}' for n in article_nums)} constitution"
        emb = self._embed(search_q)
        lim = max(cfg["max_chunks"], 5)

        pattern_hits = self.repo.search_chunks_patterns(patterns, self.category, lim * 2)
        article_chunks = _filter_article_chunks(pattern_hits, article_nums)
        if article_chunks:
            return article_chunks[:lim], [], []

        vector_hits = self.repo.search_vector(emb, self.category, cfg["vector_limit"] + 2)
        text_hits = self.repo.search_text(search_q, self.category, cfg["text_limit"])
        fallback = _filter_article_chunks(
            list(vector_hits) + list(text_hits),
            article_nums,
        )
        if fallback:
            return fallback[:lim], [], []

        return _normalize_hits(pattern_hits)[:lim], [], []

    def _retrieve_president_eligibility(
        self, question: str, cfg: dict
    ) -> tuple[list, list, list]:
        """Recherche ciblée sur l'éligibilité à la présidence."""
        lim = max(cfg["max_chunks"], 6)
        eligibility_hits = self.repo.search_chunks_patterns(
            [
                "%eligibilite_president%",
                "%35 ans%",
                "%parrainage%",
                "%nationalité française%",
                "%Conditions pour être candidat%",
            ],
            self.category,
            4,
        )
        article_hits = self.repo.search_chunks_patterns(
            ["%ARTICLE 6.%", "%ARTICLE 7.%", "%ARTICLE 3.%", "%suffrage universel%"],
            self.category,
            6,
        )
        seen: set[str] = set()
        out: list = []
        for group in (
            _normalize_hits(eligibility_hits),
            _filter_article_chunks(article_hits, [6]),
            _filter_article_chunks(article_hits, [7]),
            _normalize_hits(article_hits),
        ):
            for item in group:
                key = item[0][:100]
                if key not in seen:
                    out.append(item)
                    seen.add(key)
        if out:
            return out[:lim], [], []

        emb = self._embed(
            f"{question} Président République élection éligibilité suffrage article 6 7"
        )
        vector_hits = self.repo.search_vector(emb, self.category, cfg["vector_limit"] + 2)
        text_hits = self.repo.search_text(
            "président élection éligibilité suffrage universel 35 ans parrainages",
            self.category,
            cfg["text_limit"],
        )
        return _merge_text_hits(text_hits, eligibility_hits, vector_hits, lim), [], []

    def run(
        self,
        question: str,
        display_question: str | None = None,
        conversation_context: str | None = None,
    ) -> AgentResult:
        cfg = get_multi_agent_settings()
        user_q = display_question or question
        chunks, facts, tables = self.retrieve(question, display_question=user_q)
        article_nums = _extract_article_numbers(user_q)
        history_block = ""
        if conversation_context:
            history_block = f"\n\nHISTORIQUE DE LA CONVERSATION :\n{conversation_context}\n"

        sources = []
        seen = set()
        for item in chunks:
            fname = _unpack_hit(item)[2]
            if fname not in seen:
                seen.add(fname)
                sources.append({"file": fname, "type": "document"})

        use_extractive = (
            cfg["extractive"]
            and _is_short_query(user_q)
            and chunks
            and not article_nums
            and not _needs_synthesis(user_q)
        )
        if use_extractive:
            ext = _extractive_answer(chunks, user_q, cfg["chunk_chars"])
            if ext:
                return AgentResult(answer=ext, agent=self.name, sources=sources)

        chunk_limit = 1200 if (article_nums or _is_president_eligibility_question(user_q)) else cfg["chunk_chars"]
        context = _format_chunks(chunks, max_chars=chunk_limit)
        system = SYSTEM_CONSTITUTION_ARTICLE if article_nums else self.system_prompt

        if cfg["fast"] or (not facts and not tables):
            if article_nums:
                suffix = "\nRecopie le texte exact de l'article demandé."
            elif _needs_synthesis(user_q):
                suffix = (
                    "\nRédige une réponse en phrases complètes (4 à 8 phrases). "
                    "Ne recopie pas d'extraits bruts."
                )
            else:
                suffix = "\nRéponds en 3-6 phrases maximum."
            prompt = ChatPromptTemplate.from_messages([
                ("system", system + suffix),
                ("human", "Question : {question}" + history_block + "\n\nEXTRAITS :\n{context}"),
            ])
            chain = prompt | self.llm
            answer = chain.invoke({"question": user_q, "context": context}).content
        else:
            facts_txt = _format_facts(facts)
            tables_txt = _format_tables(tables)
            prompt = ChatPromptTemplate.from_messages([
                ("system", system),
                ("human", """Question : {question}""" + history_block + """

EXTRAITS DOCUMENTS :
{context}

FAITS CHIFFRÉS :
{facts}

TABLEAUX :
{tables}"""),
            ])
            chain = prompt | self.llm
            answer = chain.invoke({
                "question": user_q,
                "context": context,
                "facts": facts_txt,
                "tables": tables_txt,
            }).content

        return AgentResult(answer=answer, agent=self.name, sources=sources)


class ConstitutionAgent(BaseSpecialistAgent):
    name = "constitution"
    category = "constitution"
    system_prompt = SYSTEM_CONSTITUTION

    def retrieve(
        self, question: str, display_question: str | None = None,
    ) -> tuple[list, list, list]:
        cfg = get_multi_agent_settings()
        intent_q = display_question or question
        if _is_president_eligibility_question(intent_q):
            return self._retrieve_president_eligibility(question, cfg)
        article_nums = _extract_article_numbers(intent_q)
        if article_nums:
            return self._retrieve_article(question, article_nums, cfg)
        return super().retrieve(question, display_question)


class ElectionsAgent(BaseSpecialistAgent):
    name = "elections"
    category = "elections"
    system_prompt = SYSTEM_ELECTIONS

    def retrieve(
        self, question: str, display_question: str | None = None,
    ) -> tuple[list, list, list]:
        cfg = get_multi_agent_settings()
        q_lower = question.lower()
        search_q = question
        date_patterns: list[str] = []
        if any(k in q_lower for k in ("date", "dates", "calendrier", "quand", "dernier", "derniere", "prochain")):
            search_q = (
                f"{question} calendrier scrutin tour présidentielle législatives "
                "européennes municipales juin avril 2024 2022 2017"
            )
            date_patterns = [
                "%calendrier%", "%présidentielle%2022%", "%législatives%2024%",
                "%européennes%2024%",
            ]

        if cfg["text_only"]:
            return _text_only_retrieve(
                self.repo, search_q, self.category, cfg, extra_patterns=date_patterns,
            )

        emb = self._embed(search_q)
        lim_v, lim_t = cfg["vector_limit"], cfg["text_limit"]
        vector_hits = self.repo.search_vector(emb, self.category, lim_v)
        text_hits = self.repo.search_text(search_q, self.category, lim_t)
        pattern_hits = (
            self.repo.search_chunks_patterns(date_patterns, self.category, 3)
            if date_patterns else []
        )

        chunks = _merge_text_hits(text_hits, pattern_hits, vector_hits, cfg["max_chunks"])
        return chunks, [], []


class JusticeAgent(BaseSpecialistAgent):
    name = "justice"
    category = "justice"
    system_prompt = SYSTEM_JUSTICE

    _PENAL_KW = (
        "crime", "délit", "delit", "contravention", "infraction", "pénal", "penal",
        "loi", "sanction", "peine", "prescription", "plainte", "prévenu", "prevenu",
        "accusé", "accuse", "correctionnel", "assises", "vol", "escroquerie",
        "viol", "meurtre", "assassinat",
    )

    def retrieve(
        self, question: str, display_question: str | None = None,
    ) -> tuple[list, list, list]:
        cfg = get_multi_agent_settings()
        q_lower = question.lower()
        search_q = question
        penal_patterns = ["%délit%", "%crime%", "%contravention%", "%viol%", "%meurtre%"]
        if any(k in q_lower for k in self._PENAL_KW):
            search_q = (
                f"{question} infraction pénale contravention délit crime "
                "article 111-1 code pénal tribunal correctionnel cour d'assises sanctions peines"
            )

        if cfg["text_only"]:
            return _text_only_retrieve(
                self.repo, search_q, self.category, cfg, extra_patterns=penal_patterns,
            )

        emb = self._embed(search_q)
        use_patterns = any(k in q_lower for k in self._PENAL_KW)
        lim = cfg["vector_limit"]
        vector_hits = self.repo.search_vector(emb, self.category, lim)
        text_hits = self.repo.search_text(search_q, self.category, lim)
        pattern_hits = (
            self.repo.search_chunks_patterns(penal_patterns, self.category, 3)
            if use_patterns else []
        )

        chunks = _merge_text_hits(text_hits, pattern_hits, vector_hits, cfg["max_chunks"])
        return chunks, [], []


class TestCiviqueAgent(BaseSpecialistAgent):
    name = "test_civique"
    category = "test_civique"
    system_prompt = SYSTEM_TEST_CIVIQUE


class DataAgent(BaseSpecialistAgent):
    name = "data"
    category = None
    system_prompt = SYSTEM_DATA

    def retrieve(self, question: str, display_question: str | None = None):
        cfg = get_multi_agent_settings()
        emb = self._embed(question)
        facts = self.repo.search_facts(question, limit=10)
        tables = self.repo.search_tables(question, limit=3)
        vector_hits = self.repo.search_vector(emb, limit=3)
        return vector_hits, facts, tables


class GeneralAgent(BaseSpecialistAgent):
    name = "general"
    category = None
    system_prompt = SYSTEM_GENERAL


AGENTS = {
    "constitution": ConstitutionAgent,
    "elections": ElectionsAgent,
    "justice": JusticeAgent,
    "test_civique": TestCiviqueAgent,
    "data": DataAgent,
    "general": GeneralAgent,
}
