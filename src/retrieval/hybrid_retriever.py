"""Recherche hybride : sémantique (vecteurs) + lexicale (BM25)."""

import hashlib
import re
import unicodedata

from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever
from langchain_core.callbacks import CallbackManagerForRetrieverRun
from pydantic import Field
from rank_bm25 import BM25Okapi

import src.bootstrap  # noqa: F401
from src.config import RETRIEVAL_CANDIDATES, SCORE_THRESHOLD, TOP_K_RESULTS
from src.retrieval.vector_store import VectorStoreManager

_STOP_WORDS = {
    "le", "la", "les", "de", "du", "des", "un", "une", "et", "est", "sont",
    "que", "qui", "dans", "pour", "par", "sur", "avec", "ce", "cette", "ces",
    "quelles", "quels", "comment", "pourquoi", "quoi", "aux", "en",
    "au", "ou", "son", "sa", "ses", "leur", "leurs", "il", "elle", "on",
    "nous", "vous", "ils", "elles", "pas", "plus", "moins", "tres", "trop",
    "sont", "quel", "quelle", "quelles", "quels",
}

_TOPIC_SYNONYMS: dict[str, list[str]] = {
    "president": ["president", "président", "chef de l'etat", "chef de l'état"],
    "droits": ["droits", "pouvoirs", "attributions", "prerogatives", "prérogatives"],
}


def _fold_accents(text: str) -> str:
    """Normalise les accents pour la recherche (president -> président)."""
    normalized = unicodedata.normalize("NFD", text.lower())
    return "".join(c for c in normalized if unicodedata.category(c) != "Mn")


def _tokenize(text: str) -> list[str]:
    """Tokenisation robuste (mots avec tirets, accents normalises)."""
    folded = _fold_accents(text)
    return re.findall(r"[a-z0-9]+(?:-[a-z0-9]+)*", folded)


def _extract_article_numbers(query: str) -> list[int]:
    """Détecte les références du type 'article 2', 'art. 5'."""
    nums = [int(n) for n in re.findall(r"(?:article|art\.?)\s*(\d+)", query, re.IGNORECASE)]
    return list(dict.fromkeys(nums))


def text_has_article(text: str, num: int) -> bool:
    """Vérifie si un texte contient un article constitutionnel précis."""
    return _doc_has_article(Document(page_content=text), num)


def _doc_has_article(doc: Document, num: int) -> bool:
    """Vérifie si un chunk contient un article constitutionnel précis."""
    text = doc.page_content
    patterns = (
        rf"(?i)\bARTICLE\s+{num}\s*[\.:\-]",
        rf"(?i)\bArt\.?\s*{num}\s*[\.:\-]",
        rf"(?i)\barticle\s+{num}\s*[\.:\-]",
        f"ARTICLE  {num}.",
        f"ARTICLE {num}.",
        f"Article {num}.",
    )
    return any(re.search(p, text) if p.startswith("(?") else p in text for p in patterns)


def _expand_query_terms(query: str) -> list[str]:
    """Ajoute des synonymes pour les questions thematiques (ex: president)."""
    folded = _fold_accents(query)
    extra: list[str] = []
    for key, synonyms in _TOPIC_SYNONYMS.items():
        if key in folded or any(s in folded for s in synonyms):
            extra.extend(synonyms)
    return list(dict.fromkeys(extra))


def _primary_search_words(query: str) -> list[str]:
    """Mots de la requete sans synonymes (pour detecter mot vs question)."""
    clean_query = query.strip().rstrip("?")
    article_matches = [
        m.group(0).lower().strip()
        for m in re.finditer(r"(?:article|art\.?)\s+\d+", clean_query, re.IGNORECASE)
    ]
    if article_matches:
        return list(dict.fromkeys(article_matches))

    words: list[str] = []
    for word in _tokenize(clean_query):
        if word in _STOP_WORDS:
            continue
        if len(word) >= 2 or word.isdigit():
            words.append(word)
    return list(dict.fromkeys(words))


def _search_words(query: str) -> list[str]:
    """Mots recherchables, avec synonymes thematiques."""
    words = _primary_search_words(query)
    words.extend(_expand_query_terms(query))
    return list(dict.fromkeys(words))


def _contains_word(text: str, word: str, prefix_ok: bool = False) -> bool:
    """Vérifie si un mot est présent (insensible aux accents)."""
    folded_text = _fold_accents(text)
    folded_word = _fold_accents(word)
    if not folded_word:
        return False
    if folded_word in folded_text:
        return True
    pattern = rf"(?<![a-z0-9]){re.escape(folded_word)}(?![a-z0-9])"
    if re.search(pattern, folded_text):
        return True
    if prefix_ok and len(folded_word) >= 3:
        return bool(re.search(rf"(?<![a-z0-9]){re.escape(folded_word)}", folded_text))
    return False


def _important_terms(query: str) -> list[str]:
    """Extrait les termes utiles pour la recherche (ignore les mots vides français)."""
    return _search_words(query)


def _keyword_boost(doc: Document, terms: list[str]) -> float:
    if not terms:
        return 0.0
    return sum(0.5 for term in terms if _contains_word(doc.page_content, term))


def _doc_matches_terms(doc: Document, terms: list[str], min_matches: int = 1) -> bool:
    if not terms:
        return True
    hits = sum(1 for term in terms if _contains_word(doc.page_content, term))
    return hits >= min_matches


def _literal_word_search(
    docs: list[Document], words: list[str]
) -> list[tuple[Document, float]]:
    """Recherche exacte : trouve les chunks contenant le(s) mot(s)."""
    if not words:
        return []
    hits: list[tuple[Document, float]] = []
    use_prefix = len(words) == 1 and len(words[0]) <= 5
    for doc in docs:
        matches = sum(
            1 for w in words
            if _contains_word(doc.page_content, w, prefix_ok=use_prefix)
        )
        if matches == len(words):
            score = 3.0 + matches * 0.5
            hits.append((doc, score))
        elif len(words) == 1 and matches == 1:
            hits.append((doc, 3.0))
        elif matches >= max(1, len(words) // 2):
            hits.append((doc, 2.0 + matches * 0.3))
    hits.sort(key=lambda x: x[1], reverse=True)
    return hits


def _doc_key(doc: Document) -> str:
    return hashlib.md5(doc.page_content.encode()).hexdigest()


class HybridRetriever(BaseRetriever):
    """Combine recherche vectorielle et BM25, filtre les passages peu pertinents."""

    vector_store: VectorStoreManager = Field(...)
    k: int = Field(default=TOP_K_RESULTS)
    fetch_k: int = Field(default=RETRIEVAL_CANDIDATES)
    alpha: float = Field(default=0.65, description="Poids sémantique (0-1)")
    score_threshold: float = Field(default=SCORE_THRESHOLD)

    class Config:
        arbitrary_types_allowed = True

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._bm25: BM25Okapi | None = None
        self._bm25_docs: list[Document] = []
        self._tokenized_corpus: list[list[str]] = []

    def _build_bm25(self) -> None:
        self._bm25_docs = self.vector_store.get_all_documents()
        if not self._bm25_docs:
            return
        self._tokenized_corpus = [_tokenize(doc.page_content) for doc in self._bm25_docs]
        self._bm25 = BM25Okapi(self._tokenized_corpus)

    def _rank_documents(self, query: str) -> list[tuple[Document, float]]:
        if self._bm25 is None:
            self._build_bm25()

        if not self._bm25_docs:
            docs = self.vector_store.similarity_search(query, k=self.k)
            return [(d, 1.0) for d in docs]

        key_terms = _important_terms(query)
        article_nums = _extract_article_numbers(query)

        if article_nums:
            article_hits: list[tuple[Document, float]] = []
            for doc in self._bm25_docs:
                if any(_doc_has_article(doc, n) for n in article_nums):
                    score = 2.0 + _keyword_boost(doc, key_terms)
                    article_hits.append((doc, score))
            article_hits.sort(key=lambda x: x[1], reverse=True)
            return article_hits[: self.k]

        folded_query = _fold_accents(query)
        if "president" in folded_query and any(
            t in folded_query for t in ("droit", "pouvoir", "attribution", "prerogative", "role", "fonction")
        ):
            president_hits: list[tuple[Document, float]] = []
            for doc in self._bm25_docs:
                text = _fold_accents(doc.page_content)
                if "defenseur des droits" in text:
                    continue
                score = 0.0
                if "titre ii" in text and "president" in text:
                    score = 3.5
                for n in range(5, 20):
                    if _doc_has_article(doc, n):
                        score = max(score, 3.0 + n * 0.01)
                if score == 0.0 and "president de la republique" in text:
                    score = 2.5
                if score > 0:
                    score += _keyword_boost(doc, key_terms)
                    president_hits.append((doc, score))
            if president_hits:
                president_hits.sort(key=lambda x: x[1], reverse=True)
                return president_hits[: self.k]

        primary = _primary_search_words(query)
        if 1 <= len(primary) <= 2:
            literal_hits = _literal_word_search(self._bm25_docs, primary)
            if literal_hits:
                return literal_hits[: self.k]

        tokenized_query = [t for t in _tokenize(query) if t not in _STOP_WORDS]
        if not tokenized_query:
            tokenized_query = _tokenize(query)
        bm25_scores = self._bm25.get_scores(tokenized_query)
        max_bm25 = max(bm25_scores) if len(bm25_scores) else 1.0
        alpha = 0.35 if key_terms else self.alpha

        semantic_results = self.vector_store.similarity_search_with_score(
            query, k=min(self.fetch_k, len(self._bm25_docs))
        )
        semantic_scores: dict[str, float] = {}
        for doc, distance in semantic_results:
            sem_score = 1.0 / (1.0 + distance)
            semantic_scores[_doc_key(doc)] = sem_score

        combined: dict[str, tuple[Document, float]] = {}
        for i, doc in enumerate(self._bm25_docs):
            key = _doc_key(doc)
            bm25_norm = bm25_scores[i] / (max_bm25 + 1e-9)
            sem_score = semantic_scores.get(key, 0.0)
            final_score = alpha * sem_score + (1 - alpha) * bm25_norm
            final_score += _keyword_boost(doc, key_terms)
            if final_score >= self.score_threshold:
                combined[key] = (doc, final_score)

        for doc, distance in semantic_results:
            key = _doc_key(doc)
            if key not in combined:
                sem_score = 1.0 / (1.0 + distance)
                final_score = sem_score * alpha + _keyword_boost(doc, key_terms)
                if final_score >= self.score_threshold:
                    combined[key] = (doc, final_score)

        ranked = sorted(combined.values(), key=lambda x: x[1], reverse=True)
        results = ranked[: self.k]

        if key_terms and len(key_terms) <= 2:
            filtered = [
                (d, s) for d, s in results
                if _doc_matches_terms(d, key_terms, min_matches=1)
            ]
            if filtered:
                results = filtered

        return results

    def search_word(self, word: str, limit: int | None = None) -> list[tuple[Document, float]]:
        """Recherche tous les passages contenant un mot."""
        if self._bm25 is None:
            self._build_bm25()
        clean = word.strip("?.,!:;\"'()[]").lower()
        hits = _literal_word_search(self._bm25_docs, [clean]) if clean else []
        n = limit or self.k
        return hits[:n]

    def retrieve_scored(self, query: str) -> list[tuple[Document, float]]:
        """Recherche avec scores de pertinence."""
        if self._bm25 is None:
            self._build_bm25()
        return self._rank_documents(query)

    def _get_relevant_documents(
        self, query: str, *, run_manager: CallbackManagerForRetrieverRun
    ) -> list[Document]:
        return [doc for doc, _ in self._rank_documents(query)]

    def refresh(self) -> None:
        """Reconstruit l'index BM25 après réindexation."""
        self._bm25 = None
        self._bm25_docs = []
        self._tokenized_corpus = []
