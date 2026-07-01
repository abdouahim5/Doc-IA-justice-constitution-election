from src.db.engine import get_session
from sqlalchemy import text

with get_session() as s:
    rows = s.execute(
        text(
            "SELECT fact_key, fact_value, LEFT(context, 80) "
            "FROM structured_facts sf JOIN sources s ON sf.source_id = s.id "
            "WHERE s.category = 'elections' "
            "AND (fact_value ILIKE '%2024%' OR fact_value ILIKE '%2022%' "
            "OR context ILIKE '%juin%' OR fact_key ILIKE '%date%') "
            "LIMIT 25"
        )
    ).fetchall()
    print("facts:", len(rows))
    for r in rows:
        print(r)

    chunks = s.execute(
        text(
            "SELECT s.filename, LEFT(c.content, 120) "
            "FROM document_chunks c JOIN sources s ON c.source_id = s.id "
            "WHERE s.category = 'elections' "
            "AND (c.content ILIKE '%juin 2024%' OR c.content ILIKE '%avril 2022%' "
            "OR c.content ILIKE '%9 juin%' OR c.content ILIKE '%calendrier%') "
            "LIMIT 10"
        )
    ).fetchall()
    print("\nchunks with dates:", len(chunks))
    for c in chunks:
        print(c)
