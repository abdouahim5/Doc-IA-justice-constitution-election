from src.db.engine import get_session
from sqlalchemy import text

with get_session() as s:
    rows = s.execute(
        text("SELECT filename, filepath FROM sources WHERE filepath LIKE '%calendrier%'")
    ).fetchall()
    print("calendrier sources:", rows)
    n = s.execute(
        text(
            "SELECT COUNT(*) FROM document_chunks dc "
            "JOIN sources s ON dc.source_id = s.id "
            "WHERE s.filepath LIKE '%calendrier%'"
        )
    ).scalar()
    print("chunks:", n)
