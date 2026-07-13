"""Chaînes LCEL LangChain — prompts, historique, génération."""

from __future__ import annotations

from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory

_HISTORY_STORE: dict[str, InMemoryChatMessageHistory] = {}


def history_to_messages(history: list[dict], max_turns: int = 4) -> list:
    """Convertit l'historique Streamlit en messages LangChain."""
    if not history:
        return []
    recent = history[-max_turns * 2 :]
    messages: list = []
    for msg in recent:
        role = msg.get("role")
        content = str(msg.get("content", "")).strip()
        if not content:
            continue
        if role == "user":
            messages.append(HumanMessage(content=content[:600]))
        elif role == "assistant":
            messages.append(AIMessage(content=content[:600]))
    return messages


def _get_history_store(session_id: str) -> InMemoryChatMessageHistory:
    if session_id not in _HISTORY_STORE:
        _HISTORY_STORE[session_id] = InMemoryChatMessageHistory()
    return _HISTORY_STORE[session_id]


def sync_history_store(session_id: str, history: list[dict]) -> None:
    """Aligne le store LangChain sur l'historique Streamlit."""
    store = _get_history_store(session_id)
    store.clear()
    for msg in history_to_messages(history):
        store.add_message(msg)


def build_qa_chain(llm, with_facts_tables: bool = False):
    """Chaîne LCEL : prompt (+ historique) | llm | texte."""
    if with_facts_tables:
        prompt = ChatPromptTemplate.from_messages([
            ("system", "{system_prompt}"),
            MessagesPlaceholder("history"),
            ("human", """Question : {question}

EXTRAITS DOCUMENTS :
{context}

FAITS CHIFFRÉS :
{facts}

TABLEAUX :
{tables}"""),
        ])
    else:
        prompt = ChatPromptTemplate.from_messages([
            ("system", "{system_prompt}"),
            MessagesPlaceholder("history"),
            ("human", "Question : {question}\n\nEXTRAITS :\n{context}"),
        ])
    return prompt | llm | StrOutputParser()


def invoke_qa_chain(
    llm,
    *,
    system_prompt: str,
    question: str,
    context: str,
    history: list[dict] | None = None,
    facts: str = "",
    tables: str = "",
    with_facts_tables: bool = False,
    session_id: str | None = None,
) -> str:
    """Exécute la chaîne QA avec historique LangChain natif."""
    chain = build_qa_chain(llm, with_facts_tables=with_facts_tables)
    payload = {
        "system_prompt": system_prompt,
        "question": question,
        "context": context,
        "history": history_to_messages(history or []),
        "facts": facts,
        "tables": tables,
    }
    if session_id:
        sync_history_store(session_id, history or [])
        wrapped = RunnableWithMessageHistory(
            chain,
            _get_history_store,
            input_messages_key="question",
            history_messages_key="history",
        )
        return wrapped.invoke(payload, config={"configurable": {"session_id": session_id}})
    return chain.invoke(payload)
