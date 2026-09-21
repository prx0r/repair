"""Repair → POWKernel export adapter.

Delegates to prx0r/powk's repair_adapter for canonical format.
Falls back to local export if powk is not available.

For Layer 1, this is a read-only bridge — it doesn't modify repair data.
"""

import sys
from pathlib import Path

# Ensure powk is importable
POWK_DIR = Path(__file__).parent.parent.parent / 'powk'
_powk_available = False
if POWK_DIR.exists():
    sys.path.insert(0, str(POWK_DIR))
    try:
        from adapters.repair_adapter import export as powk_export
        _powk_available = True
    except ImportError:
        pass


def export_all(output_dir: str = None) -> dict:
    """Export repair data to powk canonical format.

    Reads from repair's SQLite database.
    Writes JSONL files to output_dir (default: powk/exports/repair/).
    """
    if _powk_available:
        kwargs = {}
        if output_dir:
            kwargs['output_dir'] = output_dir
        return powk_export(**kwargs)
    else:
        return _fallback_export(output_dir)


def _fallback_export(output_dir: str = None) -> dict:
    """Minimal fallback export if powk is not available."""
    import json
    from shared.persist import get_db

    out = Path(output_dir) if output_dir else Path(__file__).parent / 'k1_export'
    out.mkdir(parents=True, exist_ok=True)

    conn = get_db()
    stats = {"nodes": 0, "edges": 0, "observations": 0, "evidence": 0}

    # Export categories as nodes
    rows = conn.execute("""
        SELECT DISTINCT normalized_json FROM source_record
        WHERE source_id = 'open_repair' AND valid = 1
        LIMIT 5000
    """).fetchall()

    categories = set()
    for (nj,) in rows:
        try:
            d = json.loads(nj)
            cat = d.get('product_category', '')
            if cat:
                categories.add(cat)
        except:
            pass

    with open(out / 'nodes.jsonl', 'w') as f:
        for cat in sorted(categories):
            node = {"id": f"repair:category:{cat.lower().replace(' ', '_')}",
                    "kind": "category", "label": cat}
            f.write(json.dumps(node) + "\n")
            stats["nodes"] += 1

    conn.close()
    print(f"Exported (fallback): {stats}")
    return stats


if __name__ == '__main__':
    result = export_all()
    print(f"Done: {result}")
