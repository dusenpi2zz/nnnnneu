"""Offline, packaged catalog with explicit evidence and implementation states."""
import json
from importlib.resources import files


def find_methods(query="", domain=None):
    records = json.loads(files("neuro_methods").joinpath("data/catalog.json").read_text(encoding="utf-8"))
    return [r for r in records if (domain is None or r["domain"] == domain)
            and query.casefold() in json.dumps(r, ensure_ascii=False).casefold()]


def get_method(method_id):
    for record in find_methods():
        if record["id"] == method_id:
            return record
    raise ValueError(f"Unknown method: {method_id}")


def read_card(method_id):
    record = get_method(method_id)
    return files("neuro_methods").joinpath("data/cards", record["card"]).read_text(encoding="utf-8")
