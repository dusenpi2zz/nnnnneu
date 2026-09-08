"""Optional LFPy forward-model demonstration; no biological parameter inference."""
from importlib.metadata import version
from pathlib import Path
import platform

import numpy as np

from . import __version__
from .workflows import _now, code_fingerprint, sha256, write_json


MORPHOLOGY = """create soma, dend
connect dend(0), soma(1)
soma {
  nseg = 1
  Ra = 150
  cm = 1
  pt3dclear()
  pt3dadd(0, 0, -10, 20)
  pt3dadd(0, 0, 10, 20)
}
dend {
  nseg = 21
  Ra = 150
  cm = 1
  pt3dclear()
  pt3dadd(0, 0, 10, 2)
  pt3dadd(0, 0, 410, 2)
}
"""


def run_lfpy_demo(output, *, dt_ms=0.0625, sigma=0.3):
    """Simulate a passive soma/dendrite model and test conductivity scaling.

    Spatial units: um; time: ms; current: nA; potential: mV; sigma: S/m.
    The built-in morphology and protocol are synthetic and not fitted to data.
    """
    if not np.isfinite(dt_ms) or not 0 < dt_ms <= 0.25:
        raise ValueError("dt_ms must be finite and in (0, 0.25]")
    if not np.isfinite(sigma) or sigma <= 0:
        raise ValueError("sigma must be finite and positive")
    try:
        from LFPy import Cell, Synapse, LineSourcePotential
        import neuron  # noqa: F401; explicit dependency diagnostic
    except ImportError as exc:
        raise ValueError("LFPy/NEURON unavailable. Use the independent Linux environment in docs/LFPY.md.") from exc
    output = Path(output).resolve()
    if output.exists():
        raise FileExistsError(f"Choose a new output directory: {output}")
    output.mkdir(parents=True)
    morphology = output / "morphology.hoc"
    morphology.write_text(MORPHOLOGY, encoding="utf-8")
    config = {"schema_version": 1, "workflow": "lfpy-passive-demo", "data_kind": "synthetic",
              "parameters": {"dt_ms": dt_ms, "sigma_s_per_m": sigma, "tstop_ms": 60.0,
              "tstart_ms": -50.0, "Ra_ohm_cm": 150.0, "cm_uF_per_cm2": 1.0,
              "g_pas_S_per_cm2": 1 / 30000, "e_pas_mV": -65.0,
              "synapse": {"type": "Exp2Syn", "weight_uS": 0.002, "tau1_ms": 0.5,
                          "tau2_ms": 3.0, "e_mV": 0.0, "event_times_ms": [20.0, 40.0]},
              "electrode_xyz_um": [[50., 0., 100.], [100., 0., 100.], [200., 0., 100.]]}}
    write_json(output / "config.resolved.json", config)
    manifest = {"schema_version": 1, "workflow": config["workflow"], "status": "running",
                "package_version": __version__, "code_sha256": code_fingerprint(), "started_at": _now(),
                "config": config, "inputs": {"morphology": {"path": str(morphology), "sha256": sha256(morphology)}},
                "environment": {"python": platform.python_version(), "numpy": np.__version__,
                                "platform": platform.platform(), "LFPy": version("LFPy"), "neuron": version("neuron")},
                "evidence_level": "synthetic_forward_model_check"}
    write_json(output / "manifest.json", manifest)
    try:
        cell = Cell(morphology=str(morphology), passive=True,
                    passive_parameters={"g_pas": 1 / 30000, "e_pas": -65.0},
                    v_init=-65.0, Ra=150.0, cm=1.0, dt=dt_ms,
                    tstart=-50.0, tstop=60.0, nsegs_method=None)
        synapse = Synapse(cell=cell, idx=int(cell.get_idx("dend")[-1]), syntype="Exp2Syn",
                          weight=0.002, tau1=0.5, tau2=3.0, e=0.0, record_current=True)
        synapse.set_spike_times(np.array([20., 40.]))
        electrodes = np.asarray(config["parameters"]["electrode_xyz_um"])
        coords = {"x": electrodes[:, 0], "y": electrodes[:, 1], "z": electrodes[:, 2]}
        probe = LineSourcePotential(cell=cell, sigma=sigma, **coords)
        cell.simulate(probes=[probe], rec_imem=True)
        double_sigma = LineSourcePotential(cell=cell, sigma=2 * sigma, **coords)
        scaled = double_sigma.get_transformation_matrix() @ cell.imem
        arrays = {"time_ms": np.asarray(cell.tvec), "soma_mV": np.asarray(cell.somav),
                  "synapse_current_nA": np.asarray(synapse.i), "extracellular_mV": np.asarray(probe.data),
                  "membrane_current_nA": np.asarray(cell.imem), "electrode_xyz_um": electrodes}
        if not all(np.isfinite(a).all() for a in arrays.values()):
            raise ValueError("Nonfinite simulation output")
        if arrays["extracellular_mV"].shape != (3, len(arrays["time_ms"])):
            raise ValueError("Unexpected electrode/time dimensions")
        if np.max(np.abs(arrays["extracellular_mV"])) < 1e-12:
            raise ValueError("No measurable response in synthetic protocol")
        scaling_error = float(np.max(np.abs(scaled - arrays["extracellular_mV"] / 2)))
        if not np.allclose(scaled, arrays["extracellular_mV"] / 2, rtol=1e-9, atol=1e-12):
            raise ValueError("Conductivity scaling check failed")
        summary = {"n_electrodes": 3, "n_timepoints": len(cell.tvec), "trace_axes": ["electrode", "time"],
                   "extracellular_unit": "mV", "dt_ms": dt_ms,
                   "max_abs_extracellular_mV": float(np.max(np.abs(probe.data))),
                   "conductivity_scaling_max_error_mV": scaling_error,
                   "max_abs_total_membrane_current_nA": float(np.max(np.abs(cell.imem.sum(axis=0)))),
                   "checks": {"finite": True, "nonzero_response": True, "inverse_sigma_scaling": True},
                   "boundary": "Synthetic passive forward model; no biological validation, EEG head model or inverse inference."}
        np.savez_compressed(output / "results.npz", **arrays)
        write_json(output / "summary.json", summary)
        try:
            import matplotlib
            matplotlib.use("Agg")
            import matplotlib.pyplot as plt
        except ImportError:
            summary["preview"] = "not_generated: install plot extra"
        else:
            fig, axes = plt.subplots(2, 1, figsize=(9, 6), sharex=True)
            axes[0].plot(cell.tvec, cell.somav)
            axes[0].set(ylabel="Soma potential (mV)", title="LFPy passive model: synthetic demonstration")
            for i, x in enumerate(electrodes[:, 0]):
                axes[1].plot(cell.tvec, probe.data[i] * 1000, label=f"x={x:g} um")
            axes[1].set(xlabel="Time (ms)", ylabel="Extracellular potential (uV)")
            axes[1].legend()
            fig.tight_layout()
            fig.savefig(output / "preview.png", dpi=150)
            plt.close(fig)
            summary["preview"] = "preview.png"
        write_json(output / "summary.json", summary)
        (output / "report.md").write_text("# LFPy run review\n\nSynthetic passive forward model. Scientific review pending.\n\n"
            "- [ ] Check morphology, units, synapse and electrode geometry\n"
            "- [ ] Repeat with smaller dt and finer spatial discretization\n"
            "- [ ] Compare conductivity, boundaries and measurement assumptions\n"
            "- [ ] State which observations the model can and cannot explain\n", encoding="utf-8")
        manifest.update(status="completed_needs_review", finished_at=_now(),
            outputs={p.name: sha256(p) for p in output.iterdir() if p.is_file() and p.name != "manifest.json"})
        write_json(output / "manifest.json", manifest)
    except Exception as exc:
        manifest.update(status="failed", finished_at=_now(), error={"type": type(exc).__name__, "message": str(exc)})
        write_json(output / "manifest.json", manifest)
        raise
    return output
