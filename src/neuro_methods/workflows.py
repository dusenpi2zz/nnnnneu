"""Configuration-driven runs with input hashes, manifests and safe numeric loading."""
import hashlib
import json
import platform
from datetime import datetime, timezone
from importlib.resources import files
from pathlib import Path

import numpy as np

from . import __version__
from .signals import delta_f_over_f, extract_roi_traces, numeric_array, pearson_connectivity, trace_qc


def _now():
    return datetime.now(timezone.utc).isoformat()


def sha256(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def code_fingerprint():
    digest = hashlib.sha256()
    for item in sorted(files("neuro_methods").iterdir(), key=lambda p: p.name):
        if item.name.endswith(".py"):
            digest.update(item.name.encode())
            digest.update(item.read_bytes())
    return digest.hexdigest()


def write_json(path, content):
    Path(path).write_text(json.dumps(content, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def _load_numeric(path):
    if Path(path).suffix.lower() != ".npy":
        raise ValueError("v0.1 accepts numeric .npy inputs only; convert other formats explicitly")
    return np.load(path, allow_pickle=False, mmap_mode="r")


def _resolve_config(config_path):
    path = Path(config_path).resolve()
    config = json.loads(path.read_text(encoding="utf-8-sig"))
    allowed = {"schema_version", "workflow", "inputs", "sampling_rate_hz", "parameters", "data_kind", "upstream"}
    if not isinstance(config, dict) or set(config) - allowed:
        raise ValueError("Unknown configuration fields")
    if config.get("schema_version") != 1:
        raise ValueError("schema_version must be 1")
    workflow = config.get("workflow")
    expected = {"roi-dff": {"movie", "masks"}, "suite2p-dff": {"F", "Fneu", "iscell"}, "pearson": {"traces"}}
    if workflow not in expected:
        raise ValueError(f"Unsupported workflow: {workflow}")
    inputs = config.get("inputs")
    if not isinstance(inputs, dict) or set(inputs) != expected[workflow]:
        raise ValueError(f"inputs must be exactly {sorted(expected[workflow])}")
    for name, value in inputs.items():
        if not isinstance(value, str):
            raise ValueError("input paths must be strings")
        resolved = (path.parent / value).resolve()
        if not resolved.is_file():
            raise ValueError(f"Missing input {name}: {resolved}")
        inputs[name] = str(resolved)
    rate = config.get("sampling_rate_hz")
    if isinstance(rate, bool) or not isinstance(rate, (float, int)) or not np.isfinite(rate) or rate <= 0:
        raise ValueError("sampling_rate_hz must be a positive finite number")
    if config.get("data_kind") not in {"synthetic", "public", "restricted", "local"}:
        raise ValueError("data_kind must be synthetic/public/restricted/local")
    parameters = config.setdefault("parameters", {})
    valid_parameters = {"roi-dff": {"percentile", "min_baseline", "motion_corrected", "chunk_frames"},
                        "suite2p-dff": {"percentile", "min_baseline", "neuropil_coefficient", "cells_only"},
                        "pearson": set()}
    if not isinstance(parameters, dict) or set(parameters) - valid_parameters[workflow]:
        raise ValueError("Unsupported parameters for selected workflow")
    if workflow != "pearson":
        parameters.setdefault("percentile", 20)
        parameters.setdefault("min_baseline", 1e-6)
    if workflow == "roi-dff":
        parameters.setdefault("chunk_frames", 128)
    if workflow == "roi-dff" and parameters.get("motion_corrected") is not True:
        raise ValueError("roi-dff requires motion_corrected=true after external visual QC")
    if workflow == "suite2p-dff":
        alpha = parameters.get("neuropil_coefficient")
        if isinstance(alpha, bool) or not isinstance(alpha, (float, int)) or not np.isfinite(alpha) or not 0 <= alpha <= 1:
            raise ValueError("Explicit neuropil_coefficient in [0,1] required; no automatic choice")
        if not isinstance(parameters.get("cells_only"), bool):
            raise ValueError("Explicit boolean cells_only required")
        upstream = config.get("upstream", {})
        if not isinstance(upstream, dict) or not isinstance(upstream.get("suite2p_version"), str) or not upstream["suite2p_version"].strip():
            raise ValueError("Record upstream.suite2p_version (or explicitly 'unknown')")
    return config, path


def _plot(output, arrays, rate, workflow):
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        return "not_generated: install the plot extra"
    if workflow == "pearson":
        fig, ax = plt.subplots(figsize=(6, 5))
        img = ax.imshow(arrays["correlation"], vmin=-1, vmax=1, cmap="coolwarm")
        fig.colorbar(img, ax=ax, label="Pearson r")
        ax.set(xlabel="ROI index", ylabel="ROI index", title="Descriptive correlation; no causal inference")
    else:
        traces = arrays["dff"]
        fig, ax = plt.subplots(figsize=(10, 4))
        for i, row in enumerate(traces[:8]):
            ax.plot(np.arange(len(row)) / rate, row, label=f"ROI {int(arrays['roi_ids'][i])}")
        ax.set(xlabel="Time (s)", ylabel="Delta F / F0", title="Trace preview (up to 8 ROIs); visual QC still required")
        ax.legend(loc="upper right")
    fig.tight_layout()
    fig.savefig(output / "preview.png", dpi=150)
    plt.close(fig)
    return "preview.png"


def run_config(config_path, output):
    """Run a supported workflow. Existing output directories are never overwritten."""
    config, source = _resolve_config(config_path)
    output = Path(output).resolve()
    if output.exists():
        raise FileExistsError(f"Choose a new output directory: {output}")
    input_records = {k: {"path": v, "sha256": sha256(v)} for k, v in config["inputs"].items()}
    manifest = {"schema_version": 1, "package_version": __version__, "code_sha256": code_fingerprint(), "started_at": _now(),
                "status": "running", "workflow": config["workflow"], "config": config,
                "config_source_sha256": sha256(source), "inputs": input_records,
                "environment": {"python": platform.python_version(), "numpy": np.__version__,
                                "platform": platform.platform()},
                "evidence_level": "synthetic_software_check" if config["data_kind"] == "synthetic" else "unreviewed_run"}
    output.mkdir(parents=True)
    write_json(output / "manifest.json", manifest)
    write_json(output / "config.resolved.json", config)
    try:
        inputs, params, workflow = config["inputs"], config["parameters"], config["workflow"]
        warnings = ["Successful execution does not establish scientific validity; inspect assumptions and QC."]
        arrays = {}
        if workflow == "pearson":
            traces = numeric_array(_load_numeric(inputs["traces"]), 2, "traces", min_time=3)
            arrays = {"correlation": pearson_connectivity(traces)}
            warnings += ["No nuisance regression, filtering, null model or multiple-testing correction is performed.",
                         "Correlation does not identify causal or anatomical connections."]
        else:
            if workflow == "roi-dff":
                traces = extract_roi_traces(_load_numeric(inputs["movie"]), _load_numeric(inputs["masks"]),
                                           params.get("chunk_frames", 128))
                arrays["roi_ids"] = np.arange(len(traces))
                arrays["fluorescence"] = traces
                warnings += ["Registration, ROI detection, demixing and neuropil correction are external prerequisites or limitations."]
            else:
                raw = numeric_array(_load_numeric(inputs["F"]), 2, "F", min_time=3)
                neuropil = numeric_array(_load_numeric(inputs["Fneu"]), 2, "Fneu", min_time=3)
                iscell = numeric_array(_load_numeric(inputs["iscell"]), 2, "iscell")
                if raw.shape != neuropil.shape or iscell.shape != (len(raw), 2):
                    raise ValueError("Suite2p F/Fneu/iscell dimensions disagree")
                if not np.isin(iscell[:, 0], [0, 1]).all() or np.any((iscell[:, 1] < 0) | (iscell[:, 1] > 1)):
                    raise ValueError("iscell must contain binary labels and probabilities in [0,1]")
                ids = np.flatnonzero(iscell[:, 0] == 1) if params["cells_only"] else np.arange(len(raw))
                if len(ids) == 0:
                    raise ValueError("No ROIs remain after iscell selection")
                traces = raw[ids] - params["neuropil_coefficient"] * neuropil[ids]
                arrays.update(roi_ids=ids, fluorescence=raw[ids], neuropil=neuropil[ids],
                              corrected_fluorescence=traces, iscell=iscell[ids])
                warnings += ["Suite2p extraction was not run here; numeric output import only.",
                             "Global-percentile dF/F is this package's transform, not Suite2p's inferred activity."]
            dff, baseline = delta_f_over_f(traces, params.get("percentile", 20), params.get("min_baseline", 1e-6))
            arrays.update(dff=dff, baseline=baseline)
            warnings += ["A global percentile baseline may be inappropriate with bleaching/drift or sustained activity.",
                         "Fluorescence and dF/F are not directly measured spike trains."]
        qc = trace_qc(traces)
        if qc["constant_roi_indices"]:
            warnings.append("Constant traces detected; review ROI selection.")
        np.savez_compressed(output / "results.npz", **arrays)
        summary = {"workflow": workflow, "sampling_rate_hz": config["sampling_rate_hz"],
                   "trace_axes": ["roi", "time"], "qc": qc, "warnings": warnings,
                   "array_shapes": {k: list(v.shape) for k, v in arrays.items()}}
        summary["preview"] = _plot(output, arrays, config["sampling_rate_hz"], workflow)
        write_json(output / "summary.json", summary)
        lines = ["# Run review", "", f"Workflow: `{workflow}`", "", "Status: completed; scientific review pending.",
                 "", f"ROIs: {qc['n_rois']}; timepoints: {qc['n_timepoints']}.", "", "## Warnings", ""]
        lines += [f"- {w}" for w in warnings]
        lines += ["", "## Researcher's review", "", "- [ ] Input and sampling metadata checked",
                  "- [ ] Assumptions and visual QC checked", "- [ ] Sensitivity/negative controls reviewed",
                  "- [ ] Interpretation and limitations written", "", "Decision: pending", ""]
        (output / "report.md").write_text("\n".join(lines), encoding="utf-8")
        manifest.update(status="completed_needs_review", finished_at=_now(),
                        outputs={p.name: sha256(p) for p in output.iterdir() if p.is_file() and p.name != "manifest.json"})
        write_json(output / "manifest.json", manifest)
    except Exception as exc:
        manifest.update(status="failed", finished_at=_now(), error={"type": type(exc).__name__, "message": str(exc)})
        write_json(output / "manifest.json", manifest)
        raise
    return output


def replay(manifest_path, output):
    """Replay only if inputs, resolved configuration and package version match."""
    manifest_path = Path(manifest_path).resolve()
    previous = json.loads(manifest_path.read_text(encoding="utf-8"))
    if previous.get("schema_version") != 1 or previous.get("status") != "completed_needs_review":
        raise ValueError("Replay requires a completed schema-1 run")
    if previous.get("package_version") != __version__:
        raise ValueError("Package version changed; install the recorded version or create an explicitly new run")
    if previous.get("code_sha256") != code_fingerprint():
        raise ValueError("Package source changed; restore the recorded code or create an explicitly new run")
    for name, current in {"python": platform.python_version(), "numpy": np.__version__}.items():
        if previous["environment"].get(name) != current:
            raise ValueError(f"{name} version changed; restore the recorded environment or create a new run")
    for record in previous["inputs"].values():
        if sha256(record["path"]) != record["sha256"]:
            raise ValueError("Input hash changed; refusing replay")
    config_path = manifest_path.parent / "config.resolved.json"
    if sha256(config_path) != previous["outputs"]["config.resolved.json"]:
        raise ValueError("Resolved configuration hash changed; refusing replay")
    if previous["workflow"] == "lfpy-passive-demo":
        from importlib.metadata import version
        from .lfpy_demo import run_lfpy_demo
        for name in ["LFPy", "neuron"]:
            if version(name) != previous["environment"][name]:
                raise ValueError(f"{name} version changed; restore the recorded environment")
        parameters = previous["config"]["parameters"]
        return run_lfpy_demo(output, dt_ms=parameters["dt_ms"], sigma=parameters["sigma_s_per_m"])
    return run_config(config_path, output)
