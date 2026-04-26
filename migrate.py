#!/usr/bin/env python3
import argparse
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import Engine, create_engine, text

ROOT = Path(__file__).parent
load_dotenv(ROOT / ".env")

MIGRATIONS_DIR = ROOT / "migrations"


def _drop_all_tables(engine: Engine) -> int:
    """DROP every base table in the current database (FK checks bypassed)."""
    with engine.begin() as conn:
        db_name = conn.execute(text("SELECT DATABASE()")).scalar()
        if not db_name:
            print("ERROR: no database selected on the connection", file=sys.stderr)
            return 1
        tables = [
            row[0]
            for row in conn.execute(
                text("""
                    SELECT table_name
                    FROM information_schema.tables
                    WHERE table_schema = :db AND table_type = 'BASE TABLE'
                """),
                {"db": db_name},
            ).all()
        ]
        if not tables:
            print(f"No tables to drop in `{db_name}`.")
            return 0
        conn.execute(text("SET FOREIGN_KEY_CHECKS = 0"))
        for t in tables:
            conn.execute(text(f"DROP TABLE IF EXISTS `{t}`"))
        conn.execute(text("SET FOREIGN_KEY_CHECKS = 1"))
        print(f"Dropped {len(tables)} table(s) from `{db_name}`: {', '.join(tables)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Apply pending SQL migrations from migrations/ in order.",
    )
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Drop ALL tables (incl. schema_migrations) before applying migrations.",
    )
    args = parser.parse_args()

    db_url = os.environ.get("DATABASE_URL")
    if not db_url:
        print("ERROR: DATABASE_URL env var not set", file=sys.stderr)
        return 1

    engine = create_engine(db_url)

    if args.reset:
        rc = _drop_all_tables(engine)
        if rc != 0:
            return rc

    # Ensure tracking table exists
    with engine.begin() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS schema_migrations (
                version VARCHAR(50) PRIMARY KEY,
                applied_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """))

    # Read applied versions
    with engine.connect() as conn:
        applied = {
            row[0] for row in conn.execute(text("SELECT version FROM schema_migrations"))
        }

    # Find pending files
    files = sorted(MIGRATIONS_DIR.glob("*.sql"))
    pending = [f for f in files if f.stem not in applied]

    if not pending:
        print("Database is up to date.")
        return 0

    # Apply each pending migration in its own transaction
    for path in pending:
        version = path.stem
        sql = path.read_text()
        statements = [s.strip() for s in sql.split(";") if s.strip()]
        try:
            with engine.begin() as conn:
                for stmt in statements:
                    conn.execute(text(stmt))
                conn.execute(
                    text("INSERT INTO schema_migrations (version) VALUES (:v)"),
                    {"v": version},
                )
            print(f"Applied: {version}")
        except Exception as e:
            print(f"FAILED at {version}: {e}", file=sys.stderr)
            return 1

    print(f"\nApplied {len(pending)} migration(s). Database is up to date.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
