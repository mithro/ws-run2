"""Read the one-line digest of each analysed project.

digests.tsv has a line per project written from its repository alone. digests_layout.tsv has the
revised line for each project whose summary has since been checked against the taped-out layout
(see LAYOUT_BRIEF.md); where both exist, the layout line wins.
Fields: run/CODE, verdict, what, authors, characterisation, pdk additions, flags (tab separated).
"""
import csv
from pathlib import Path

RUNS = Path(__file__).resolve().parents[1]
FIELDS = ("verdict", "what", "authors", "char", "pdk", "flags")


def _read(path):
    rows = {}
    if path.exists():
        for row in csv.reader(path.open(), delimiter="\t", quoting=csv.QUOTE_NONE):
            assert len(row) == 1 + len(FIELDS), (path.name, row[:1], len(row))
            assert row[0] not in rows, (path.name, "duplicate", row[0])
            rows[row[0]] = dict(zip(FIELDS, row[1:]))
    return rows


def load_digests():
    """Return ({run/CODE: digest}, {run/CODE whose summary was checked against the layout})."""
    digests = _read(RUNS / "digests.tsv")
    layout = _read(RUNS / "digests_layout.tsv")
    digests.update(layout)
    return digests, set(layout)
