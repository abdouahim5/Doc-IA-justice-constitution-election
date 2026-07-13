from sqlalchemy import create_engine, text
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")
url = os.environ["DATABASE_URL"].replace("-pooler.", ".")
with create_engine(url).connect() as c:
    const = c.execute(text("""
        SELECT COUNT(*) FROM document_chunks dc
        JOIN sources s ON s.id = dc.source_id WHERE s.category = 'constitution'
    """)).scalar()
    art5 = c.execute(text("""
        SELECT COUNT(*) FROM document_chunks dc
        JOIN sources s ON s.id = dc.source_id
        WHERE s.category = 'constitution' AND dc.content ILIKE '%ARTICLE 5%'
    """)).scalar()
    print(f"constitution chunks: {const}")
    print(f"article 5 hits: {art5}")
