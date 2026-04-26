import csv
from pathlib import Path

from sqlalchemy import Engine, text

EVIDENCE_DIR = Path(__file__).parent.parent / "evidence"


def snapshot_table(engine: Engine, table: str) -> list[dict]:
    """Return the full table content as a list of dicts (one per row)."""
    with engine.connect() as conn:
        rows = conn.execute(text(f"SELECT * FROM {table}")).mappings().all()
    return [dict(r) for r in rows]


def write_snapshot_csv(rows: list[dict], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("(empty table)\n")
        return
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def capture_evidence(
    engine: Engine,
    test_name: str,
    affected_tables: list[str],
    when: str,
) -> None:
    """Snapshot every table named in `affected_tables` to tests/evidence/<test_name>/<when>_<table>.csv."""
    base = EVIDENCE_DIR / test_name
    for tbl in affected_tables:
        snap = snapshot_table(engine, tbl)
        write_snapshot_csv(snap, base / f"{when}_{tbl}.csv")


def write_diff_summary(test_name: str, summary: str) -> None:
    base = EVIDENCE_DIR / test_name
    base.mkdir(parents=True, exist_ok=True)
    (base / "diff.md").write_text(summary)
