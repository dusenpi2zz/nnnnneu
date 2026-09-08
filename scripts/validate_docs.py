"""Check local Markdown links and keep catalog documentation coverage explicit."""
import json
from pathlib import Path
import re
from urllib.parse import unquote

root = Path(__file__).resolve().parents[1]
failures = []
markdown = [root / "README.md", root / "CONTRIBUTING.md", root / "NOTICE.md"]
markdown += list((root / "docs").glob("*.md"))
markdown += list((root / "src/neuro_methods/data/cards").glob("*.md"))
for path in markdown:
    for target in re.findall(r"\]\(([^)]+)\)", path.read_text(encoding="utf-8")):
        target = target.strip("<>").split("#")[0]
        if not target or "://" in target or target.startswith("mailto:"):
            continue
        if not (path.parent / unquote(target)).resolve().exists():
            failures.append(f"{path.relative_to(root)}: {target}")
rows = json.loads((root / "src/neuro_methods/data/catalog.json").read_text(encoding="utf-8"))
index = (root / "docs/CATALOG.md").read_text(encoding="utf-8")
for row in rows:
    if row["card"] not in index:
        failures.append(f"Missing catalog link: {row['id']}")
if failures:
    raise SystemExit("\n".join(failures))
print(f"Validated {len(markdown)} Markdown files and {len(rows)} catalog links")
