import json
from pathlib import Path

import numpy as np
import pytest

from neuro_methods.catalog import find_methods, read_card
from neuro_methods.cli import main
from neuro_methods.demo import make_demo
from neuro_methods.workflows import replay, run_config, write_json


def config(tmp_path, workflow="pearson"):
    np.save(tmp_path / "traces.npy", [[1., 2, 3], [3., 2, 1]])
    cfg = {"schema_version": 1, "workflow": workflow, "data_kind": "synthetic",
           "inputs": {"traces": "traces.npy"}, "sampling_rate_hz": 10, "parameters": {}}
    path = tmp_path / "config.json"
    write_json(path, cfg)
    return path, cfg


def test_run_and_replay_keep_arrays_and_input_identity(tmp_path):
    path, _ = config(tmp_path)
    first = run_config(path, tmp_path / "first")
    second = replay(first / "manifest.json", tmp_path / "second")
    with np.load(first / "results.npz") as a, np.load(second / "results.npz") as b:
        np.testing.assert_array_equal(a["correlation"], b["correlation"])
    one = json.loads((first / "manifest.json").read_text(encoding="utf-8"))
    two = json.loads((second / "manifest.json").read_text(encoding="utf-8"))
    assert one["inputs"] == two["inputs"]
    assert one["status"] == "completed_needs_review"
    assert one["code_sha256"] == two["code_sha256"]
    with pytest.raises(FileExistsError):
        run_config(path, first)


@pytest.mark.parametrize("changed", ["input", "config", "version", "source", "numpy"])
def test_replay_refuses_drift(tmp_path, changed):
    path, _ = config(tmp_path)
    run = run_config(path, tmp_path / "run")
    manifest_path = run / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if changed == "input":
        np.save(tmp_path / "traces.npy", [[1., 2, 4], [4., 3, 1]])
    elif changed == "config":
        (run / "config.resolved.json").write_text("{}")
    else:
        if changed == "version": manifest["package_version"] = "0.0.0"
        if changed == "source": manifest["code_sha256"] = "changed"
        if changed == "numpy": manifest["environment"]["numpy"] = "0.0.0"
        write_json(manifest_path, manifest)
    with pytest.raises(ValueError):
        replay(manifest_path, tmp_path / "replay")
    assert not (tmp_path / "replay").exists()


def test_failed_run_retains_failure_evidence(tmp_path):
    path, _ = config(tmp_path)
    np.save(tmp_path / "traces.npy", [[1, 1, 1], [1, 2, 3]])
    with pytest.raises(ValueError):
        run_config(path, tmp_path / "failed")
    manifest = json.loads((tmp_path / "failed/manifest.json").read_text(encoding="utf-8"))
    assert manifest["status"] == "failed"
    assert manifest["error"]["type"] == "ValueError"


def test_suite2p_import_preserves_roi_ids_and_correction(tmp_path):
    raw = np.array([[20., 30, 40], [30., 40, 50], [40., 50, 60]])
    for name, data in {"F": raw, "Fneu": np.full((3, 3), 10.),
                       "iscell": [[0, .1], [1, .9], [1, .8]]}.items():
        np.save(tmp_path / (name + ".npy"), data)
    cfg = {"schema_version": 1, "workflow": "suite2p-dff", "data_kind": "synthetic",
           "inputs": {n: n + ".npy" for n in ["F", "Fneu", "iscell"]},
           "sampling_rate_hz": 10, "parameters": {"neuropil_coefficient": .5, "cells_only": True, "percentile": 0},
           "upstream": {"suite2p_version": "synthetic-fixture"}}
    write_json(tmp_path / "config.json", cfg)
    output = run_config(tmp_path / "config.json", tmp_path / "output")
    with np.load(output / "results.npz") as result:
        np.testing.assert_array_equal(result["roi_ids"], [1, 2])
        np.testing.assert_allclose(result["corrected_fluorescence"], raw[1:] - 5)
        np.testing.assert_allclose(result["baseline"], [25, 35])
        np.testing.assert_allclose(result["dff"][0], [0, .4, .8])


def test_pickle_arrays_rejected_without_execution(tmp_path):
    path, _ = config(tmp_path)
    np.save(tmp_path / "traces.npy", np.array([{"value": 1}], dtype=object))
    with pytest.raises(ValueError):
        run_config(path, tmp_path / "output")


@pytest.mark.parametrize("field,value", [("schema_version", 2), ("workflow", "imaginary"),
                                         ("sampling_rate_hz", 0), ("sampling_rate_hz", True),
                                         ("data_kind", "imaginary"), ("parameters", {"typo": 1})])
def test_configuration_errors_fail_before_run(tmp_path, field, value):
    path, cfg = config(tmp_path)
    cfg[field] = value
    write_json(path, cfg)
    with pytest.raises(ValueError):
        run_config(path, tmp_path / "output")
    assert not (tmp_path / "output").exists()


def test_demo_meets_known_signal_acceptance(tmp_path):
    run = make_demo(tmp_path / "demo")
    result = json.loads((run / "software-check.json").read_text(encoding="utf-8"))
    assert result["passed"] and result["fluorescence_rmse"] < .15


def test_catalog_ids_cards_and_source_provenance():
    rows = find_methods()
    ids = [r["id"] for r in rows]
    assert len(ids) == len(set(ids))
    assert {"suite2p", "cellreg-jinghao", "mosaic-roi", "roi-dff", "identifiability"} <= set(ids)
    for row in rows:
        assert read_card(row["id"]).startswith("# ")
        assert Path(row["card"]).name == row["card"]
        assert row["implementation"] in {"reference_only", "implemented"}
        for source in row["sources"]:
            assert source["url"].startswith(("https://", "http://"))
            assert source["checked_on"]
    assert find_methods("单光子", "calcium")


def test_new_method_does_not_overwrite(tmp_path):
    assert main(["new-method", "test-method", "--output", str(tmp_path)]) == 0
    assert main(["new-method", "test-method", "--output", str(tmp_path)]) == 2
    assert main(["new-method", "../escape", "--output", str(tmp_path)]) == 2
