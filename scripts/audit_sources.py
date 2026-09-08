"""Read public GitHub metadata for catalogued repositories; do not infer validity from activity."""
import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import json
from pathlib import Path
import urllib.request
from urllib.parse import urlparse


def inspect(repository):
    try:
        request = urllib.request.Request("https://api.github.com/repos/" + repository,
                                         headers={"User-Agent": "neuro-methods-source-audit"})
        with urllib.request.urlopen(request, timeout=25) as stream:
            data = json.load(stream)
        result = {key: data.get(key) for key in ["full_name", "html_url", "archived", "disabled", "fork",
                   "default_branch", "pushed_at", "license"]}
        result["repository_requested"] = repository
        result["parent"] = data.get("parent", {}).get("full_name")
        result["status"] = "metadata_retrieved"
        return result
    except Exception as exc:
        return {"repository_requested": repository, "status": "error", "error": str(exc)}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    rows = json.loads((root / "src/neuro_methods/data/catalog.json").read_text(encoding="utf-8"))
    repositories = set()
    for row in rows:
        for source in row["sources"]:
            url = urlparse(source["url"])
            segments = url.path.strip("/").split("/")
            if url.hostname == "github.com" and len(segments) == 2:
                repositories.add("/".join(segments))
    output = Path(args.output)
    if output.exists():
        raise FileExistsError("Use a new snapshot path")
    with ThreadPoolExecutor(max_workers=4) as pool:
        results = list(pool.map(inspect, sorted(repositories)))
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps({"checked_at": datetime.now(timezone.utc).isoformat(),
        "boundary": "Public metadata only. Last push does not establish support, quality or compatibility.",
        "repositories": results}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"repositories": len(results), "errors": sum(r["status"] == "error" for r in results)}))


if __name__ == "__main__":
    main()
