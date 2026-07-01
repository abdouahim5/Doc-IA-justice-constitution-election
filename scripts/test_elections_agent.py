from src.db.engine import get_session
from src.db.repository import CorpusRepository
from src.multi_agent.agents import ElectionsAgent

question = "dates des derniers elections"
session = get_session()
repo = CorpusRepository(session)
agent = ElectionsAgent(session, repo)
chunks, facts, tables = agent.retrieve(question)
print("chunks:", len(chunks))
for item in chunks[:5]:
    if isinstance(item[0], str):
        content, score, fname = item[0], item[1], item[2]
    else:
        content = item[0].content[:200]
        score, fname = item[1], item[2]
    print(f"\n--- {fname} ({score:.2f}) ---\n{content[:300]}")
print("\nfacts:", len(facts))
for f in facts[:8]:
    print(f"  {f.fact_key}: {f.fact_value} | {f.context[:60] if f.context else ''}")
result = agent.run(question)
print("\nANSWER:\n", result.answer[:800])
