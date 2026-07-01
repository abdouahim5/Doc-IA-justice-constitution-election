"""Agent RAG conversationnel — priorité à la fiabilité des réponses."""

from dataclasses import dataclass, field

from langchain_classic.chains import create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder, PromptTemplate
from langchain_core.chat_history import InMemoryChatMessageHistory

import src.startup  # noqa: F401
from src.config import DOCUMENTS_DIR, get_rag_settings
from src.errors import format_llm_error, is_transient_error
from src.ingestion import chunk_documents, load_documents
from src.llm import get_llm
from src.retrieval import HybridRetriever, VectorStoreManager
from src.retrieval.hybrid_retriever import (
    _contains_word,
    _doc_has_article,
    _extract_article_numbers,
    _important_terms,
    _primary_search_words,
    _search_words,
)

NOT_FOUND_MSG = (
    "Cette information n'est pas présente dans les documents indexés. "
    "Essayez de reformuler votre question ou précisez le document concerné."
)

SYSTEM_PROMPT_WORD = """Tu es un moteur de recherche documentaire.

L'utilisateur cherche un mot ou une expression dans ses documents.
Liste les passages des extraits ci-dessous qui contiennent ce mot.
Pour chaque passage : cite [nom_fichier] et recopie la phrase pertinente.
Si le mot n'apparaît dans aucun extrait, dis : "Mot non trouvé dans les documents indexés."

EXTRAITS :
{context}"""

SYSTEM_PROMPT = """Tu es un assistant documentaire strict et fiable.

RÈGLES OBLIGATOIRES :
1. Lis UNIQUEMENT les extraits ci-dessous. N'utilise AUCUNE connaissance externe.
2. Si la réponse n'est pas explicitement dans les extraits, réponds EXACTEMENT :
   "Cette information n'est pas présente dans les documents indexés."
3. Ne devine pas, n'extrapole pas, ne complète pas avec ton savoir général.
4. Réponds en français, de façon claire. Cite la source : [nom_du_fichier].
5. Reprends les mots importants tels qu'ils apparaissent dans l'extrait.
6. Si les extraits sont hors sujet par rapport à la question, refuse de répondre.
7. Si la question porte sur les droits/pouvoirs d'une fonction (ex: président),
   synthétise TOUS les extraits pertinents en liste à puces, même répartis sur
   plusieurs articles.
8. Utilise l'historique de conversation pour comprendre les questions de suivi
   (ex: "et l'article 3 ?", "developpe", "le meme pour le senat").

EXTRAITS :
{context}"""

_FOLLOW_UP_MARKERS = (
    "et l'", "et la ", "et le ", "et les ", "aussi", "également", "egalement",
    "developpe", "développe", "plus de", "en savoir", "le suivant", "la suite",
    "l'autre", "celui", "celle", "qu'en est", "précise", "precise", "résume",
    "resume", "meme ", "même ", "pareil", "autre article", "et pour",
)

SYSTEM_PROMPT_ARTICLE = """Tu es un expert en lecture de documents juridiques.

La question porte sur un ARTICLE précis. Les extraits ci-dessous contiennent cet article.
Recopie et résume fidèlement le contenu de l'article demandé, en français clair.
Cite la source : [nom_du_fichier].
Utilise l'historique si la question fait reference a un echange precedent.
N'invente rien. Si l'article n'est pas dans les extraits, dis :
"Cette information n'est pas présente dans les documents indexés."

EXTRAITS :
{context}"""

DOCUMENT_PROMPT = PromptTemplate.from_template(
    "=== Source : {source} ===\n{page_content}"
)


@dataclass
class AgentResponse:
    answer: str
    sources: list[dict] = field(default_factory=list)


@dataclass
class IndexResult:
    chunks: int
    errors: list[str] = field(default_factory=list)


class RAGAgent:
    """Agent RAG fiable : vérifie la pertinence avant de répondre."""

    def __init__(self):
        settings = get_rag_settings()
        self._min_relevance = settings["min_relevance"]
        self._history_turns = settings["history_turns"]
        self.llm = get_llm()
        self.vector_store = VectorStoreManager()
        self.retriever = HybridRetriever(
            vector_store=self.vector_store, k=settings["top_k"]
        )
        self._chat_history = InMemoryChatMessageHistory()
        self._build_chain()

    def _is_article_query(self, question: str) -> bool:
        return bool(_extract_article_numbers(question))

    def _is_word_search(self, question: str) -> bool:
        if self._is_article_query(question):
            return False
        q = question.strip().rstrip("?").lower()
        if any(
            marker in q
            for marker in (
                "quels", "quelles", "quel ", "quelle ", "comment", "pourquoi",
                "droits", "pouvoirs", "attributions",
            )
        ):
            return False
        words = _primary_search_words(question)
        return 1 <= len(words) <= 2

    def _build_chain(self):
        self._qa_prompt = ChatPromptTemplate.from_messages([
            ("system", SYSTEM_PROMPT),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ])
        self._word_prompt = ChatPromptTemplate.from_messages([
            ("system", SYSTEM_PROMPT_WORD),
            ("human", "Trouve le mot ou l'expression : {input}"),
        ])
        self._article_prompt = ChatPromptTemplate.from_messages([
            ("system", SYSTEM_PROMPT_ARTICLE),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ])
        self._question_answer_chain = create_stuff_documents_chain(
            self.llm, self._qa_prompt, document_prompt=DOCUMENT_PROMPT,
        )
        self._word_answer_chain = create_stuff_documents_chain(
            self.llm, self._word_prompt, document_prompt=DOCUMENT_PROMPT,
        )
        self._article_answer_chain = create_stuff_documents_chain(
            self.llm, self._article_prompt, document_prompt=DOCUMENT_PROMPT,
        )

        self._word_rag_chain = create_retrieval_chain(
            self.retriever, self._word_answer_chain
        )
        self._article_rag_chain = create_retrieval_chain(
            self.retriever, self._article_answer_chain
        )
        self._rag_chain = create_retrieval_chain(
            self.retriever, self._question_answer_chain
        )

    def _recent_history(self) -> list:
        """Derniers messages de la conversation (limite configurable)."""
        return self._chat_history.messages[-self._history_turns :]

    def _is_follow_up(self, question: str) -> bool:
        if not self._chat_history.messages:
            return False
        q = question.strip().lower()
        if any(marker in q for marker in _FOLLOW_UP_MARKERS):
            return True
        if q.startswith(("et ", "ou ", "donc ", "alors ")):
            return True
        # Suite logique : "article 5" apres avoir parle d'un autre article
        if len(q.split()) <= 4 and _extract_article_numbers(question):
            return True
        return False

    def _contextualize_question(self, question: str) -> str:
        """Enrichit la question avec le contexte pour la recherche documentaire."""
        from src.ingestion.classifier import expand_short_query

        if self._is_follow_up(question):
            lines: list[str] = []
            for msg in self._recent_history():
                role = "Utilisateur" if msg.type == "human" else "Assistant"
                lines.append(f"{role}: {msg.content[:350]}")
            if lines:
                return (
                    f"{question}\n\n"
                    "Contexte de la conversation precedente :\n"
                    + "\n".join(lines)
                )
        return expand_short_query(question)

    def _invoke_chain(self, chain, question: str, search_query: str | None = None) -> dict:
        retrieval_input = search_query or question
        payload: dict = {"input": retrieval_input}
        if chain in (self._rag_chain, self._article_rag_chain):
            payload["chat_history"] = self._recent_history()
        return chain.invoke(payload)

    def _check_relevance(self, question: str) -> AgentResponse | None:
        """Refuse de répondre si aucun passage pertinent n'est trouvé."""
        scored = self.retriever.retrieve_scored(question)
        is_short = self._is_word_search(question)

        if not scored:
            if is_short:
                words = _primary_search_words(question)
                if words and self.retriever.search_word(words[0], limit=3):
                    return None
                return AgentResponse(
                    answer="Mot ou expression non trouvé dans les documents indexés.",
                    sources=[],
                )
            return AgentResponse(answer=NOT_FOUND_MSG, sources=[])

        key_terms = _search_words(question)
        if _extract_article_numbers(question):
            if any(
                any(_doc_has_article(doc, n) for n in _extract_article_numbers(question))
                for doc, _ in scored
            ):
                return None
        if key_terms and any(
            _contains_word(doc.page_content, t, prefix_ok=len(t) <= 5)
            for doc, _ in scored
            for t in key_terms
        ):
            return None

        if is_short and scored:
            words = _primary_search_words(question)
            if words and any(
                _contains_word(doc.page_content, words[0], prefix_ok=len(words[0]) <= 5)
                for doc, _ in scored
            ):
                return None
            if words and self.retriever.search_word(words[0], limit=3):
                return None
            return AgentResponse(
                answer="Mot ou expression non trouvé dans les documents indexés.",
                sources=[],
            )

        top_score = scored[0][1]
        if top_score < self._min_relevance:
            return AgentResponse(answer=NOT_FOUND_MSG, sources=[])

        return None

    def index_documents(self, directory=None) -> int:
        result = self.index_documents_detailed(directory)
        return result.chunks

    def index_documents_detailed(self, directory=None) -> IndexResult:
        docs_dir = directory or DOCUMENTS_DIR
        raw_docs, errors = load_documents(docs_dir)
        if not raw_docs:
            return IndexResult(chunks=0, errors=errors)
        chunks = chunk_documents(raw_docs)
        count = self.vector_store.index_documents(chunks)
        self.retriever.refresh()
        return IndexResult(chunks=count, errors=errors)

    def _refresh_connections(self) -> None:
        """Reconstruit LLM, embeddings et chaines (clients HTTP fermes par Streamlit)."""
        settings = get_rag_settings()
        self.llm = get_llm()
        self.vector_store = VectorStoreManager()
        self.retriever = HybridRetriever(
            vector_store=self.vector_store, k=settings["top_k"]
        )
        self._build_chain()

    def _select_chain(self, question: str):
        if self._is_article_query(question):
            return self._article_rag_chain
        if self._is_word_search(question):
            return self._word_rag_chain
        return self._rag_chain

    def query(self, question: str) -> AgentResponse:
        settings = get_rag_settings()
        if settings["fast_mode"] and self._is_word_search(question):
            fast = self.search_word(question.strip())
            if fast.sources:
                return fast

        search_query = self._contextualize_question(question)
        early = self._check_relevance(search_query)
        if early is not None:
            return early

        chain = self._select_chain(question)

        try:
            result = self._invoke_chain(chain, question, search_query)
        except Exception as e:
            if is_transient_error(e):
                self._refresh_connections()
                chain = self._select_chain(question)
                try:
                    result = self._invoke_chain(chain, question, search_query)
                except Exception as retry_err:
                    raise format_llm_error(retry_err) from retry_err
            else:
                raise format_llm_error(e) from e

        from langchain_core.messages import AIMessage, HumanMessage

        self._chat_history.add_message(HumanMessage(content=question))
        self._chat_history.add_message(AIMessage(content=result["answer"]))

        sources = self._extract_sources(result.get("context", []))
        return AgentResponse(answer=result["answer"], sources=sources)

    def _extract_sources(self, context: list) -> list[dict]:
        seen = set()
        sources = []
        for doc in context:
            if isinstance(doc, Document):
                source_name = doc.metadata.get("source", "inconnu")
                if source_name not in seen:
                    seen.add(source_name)
                    sources.append({
                        "file": source_name,
                        "excerpt": doc.page_content[:400] + "...",
                    })
        return sources

    def search_word(self, word: str) -> AgentResponse:
        """Recherche directe d'un mot dans tous les documents."""
        hits = self.retriever.search_word(word, limit=10)
        if not hits:
            return AgentResponse(
                answer=f'Le mot "{word}" n\'a pas été trouvé dans les documents indexés.',
                sources=[],
            )
        sources = []
        lines = [f'Passages contenant "{word}" :\n']
        for doc, _ in hits:
            src = doc.metadata.get("source", "inconnu")
            excerpt = doc.page_content[:300].replace("\n", " ")
            sources.append({"file": src, "excerpt": excerpt})
            lines.append(f"- [{src}] {excerpt}")
        return AgentResponse(answer="\n".join(lines), sources=sources)

    def get_stats(self) -> dict:
        return {
            "chunks_indexed": self.vector_store.count(),
            "documents_dir": str(DOCUMENTS_DIR),
        }

    def clear_memory(self) -> None:
        self._chat_history.clear()

    def restore_conversation(self, messages: list[dict]) -> None:
        """Restaure l'historique depuis l'interface (ex: Streamlit session)."""
        from langchain_core.messages import AIMessage, HumanMessage

        self._chat_history.clear()
        for msg in messages[-self._history_turns :]:
            if msg.get("role") == "user":
                self._chat_history.add_message(HumanMessage(content=msg["content"]))
            elif msg.get("role") == "assistant":
                self._chat_history.add_message(AIMessage(content=msg["content"]))

    def clear_index(self) -> None:
        self.vector_store.clear()
        self.retriever.refresh()

    @property
    def chat_history(self) -> list:
        return self._chat_history.messages
