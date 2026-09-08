"""Deterministic synthetic software check, never biological validation."""
from pathlib import Path
import numpy as np

from .workflows import run_config, write_json


def make_demo(output, seed=42):
    output = Path(output).resolve()
    if output.exists():
        raise FileExistsError(f"Choose a new demo directory: {output}")
    output.mkdir(parents=True)
    rng = np.random.default_rng(seed)
    n, height, width, rate = 300, 24, 24, 10.0
    masks = np.zeros((3, height, width), dtype=bool)
    for i, (row, col) in enumerate([(5, 5), (5, 17), (17, 12)]):
        masks[i, row - 2:row + 3, col - 2:col + 3] = True
    signals = np.zeros((3, n))
    for i in range(3):
        for event in [30 + 15 * i, 120 + 10 * i, 220 - 10 * i]:
            signals[i, event:] += 20 * np.exp(-np.arange(n - event) / 10)
    movie = 100 + rng.normal(0, 0.3, (n, height, width))
    for i, mask in enumerate(masks):
        movie[:, mask] += signals[i, :, None]
    np.save(output / "movie.npy", movie.astype(np.float32))
    np.save(output / "masks.npy", masks)
    np.save(output / "ground_truth_fluorescence.npy", 100 + signals)
    config = {"schema_version": 1, "workflow": "roi-dff", "data_kind": "synthetic",
              "inputs": {"movie": "movie.npy", "masks": "masks.npy"}, "sampling_rate_hz": rate,
              "parameters": {"motion_corrected": True, "percentile": 20, "chunk_frames": 64},
              "upstream": {"generator": "neuro_methods.demo", "seed": seed,
                           "assumptions": "stationary nonoverlapping ROIs; additive Gaussian noise; constant background"}}
    write_json(output / "config.json", config)
    result = run_config(output / "config.json", output / "roi-run")
    with np.load(result / "results.npz", allow_pickle=False) as data:
        recovered = data["fluorescence"]
        rmse = float(np.sqrt(np.mean((recovered - (100 + signals)) ** 2)))
        np.save(output / "traces.npy", data["dff"])
    write_json(output / "software-check.json", {"seed": seed, "fluorescence_rmse": rmse,
               "acceptance_rmse_lt": 0.15, "passed": rmse < 0.15,
               "boundary": "Known masks supplied. No cell detection, motion correction or biological validation."})
    if rmse >= 0.15:
        raise RuntimeError("Synthetic recovery check failed")
    write_json(output / "pearson.json", {"schema_version": 1, "workflow": "pearson", "data_kind": "synthetic",
               "inputs": {"traces": "traces.npy"}, "sampling_rate_hz": rate, "parameters": {}})
    run_config(output / "pearson.json", output / "pearson-run")
    return output
