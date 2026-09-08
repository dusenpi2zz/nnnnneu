import json

import numpy as np
import pytest

from neuro_methods.lfpy_demo import run_lfpy_demo
from neuro_methods.workflows import replay


def test_invalid_lfpy_parameters_fail_before_import(tmp_path):
    with pytest.raises(ValueError):
        run_lfpy_demo(tmp_path / "invalid", sigma=-1)
    with pytest.raises(ValueError):
        run_lfpy_demo(tmp_path / "invalid", dt_ms=1)
    assert not (tmp_path / "invalid").exists()


def test_lfpy_passive_model_and_replay(tmp_path):
    pytest.importorskip("LFPy")
    pytest.importorskip("neuron")
    out = run_lfpy_demo(tmp_path / "lfpy")
    summary = json.loads((out / "summary.json").read_text(encoding="utf-8"))
    assert all(summary["checks"].values())
    assert summary["conductivity_scaling_max_error_mV"] < 1e-10
    second = replay(out / "manifest.json", tmp_path / "replay")
    with np.load(out / "results.npz") as a, np.load(second / "results.npz") as b:
        np.testing.assert_allclose(a["extracellular_mV"], b["extracellular_mV"], rtol=1e-9, atol=1e-12)
