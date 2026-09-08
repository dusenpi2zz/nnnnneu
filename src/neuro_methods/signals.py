"""Explicit array semantics: traces are ROI x time; movies are time x row x col."""
import numpy as np


def numeric_array(value, ndim, name, min_time=None):
    array = np.asarray(value)
    if array.ndim != ndim or any(n == 0 for n in array.shape):
        raise ValueError(f"{name}: expected nonempty {ndim}D array")
    if array.dtype.kind not in "iuf" or not np.isfinite(array).all():
        raise ValueError(f"{name}: finite real numeric values required")
    if min_time and array.shape[-1] < min_time:
        raise ValueError(f"{name}: at least {min_time} timepoints required")
    return array.astype(np.float64, copy=False)


def extract_roi_traces(movie, masks, chunk_frames=128):
    """Mean fluorescence in non-overlapping binary masks; no registration/demixing."""
    movie = np.asanyarray(movie)
    masks = np.asarray(masks)
    if movie.ndim != 3 or any(n == 0 for n in movie.shape) or movie.dtype.kind not in "iuf":
        raise ValueError("movie: expected nonempty real time x row x col array")
    if masks.ndim != 3 or masks.shape[0] == 0 or masks.shape[1:] != movie.shape[1:]:
        raise ValueError("masks: expected ROI x row x col matching movie")
    if masks.dtype.kind not in "biuf" or not np.isin(masks, [0, 1]).all():
        raise ValueError("masks: binary 0/1 values required")
    masks = masks.astype(bool)
    if np.any(masks.sum(axis=(1, 2)) == 0):
        raise ValueError("masks: empty ROI")
    if np.any(masks.sum(axis=0) > 1):
        raise ValueError("masks overlap: this workflow does not demix overlapping sources")
    if isinstance(chunk_frames, bool) or not isinstance(chunk_frames, int) or chunk_frames < 1:
        raise ValueError("chunk_frames: positive integer required")
    result = np.empty((len(masks), len(movie)), dtype=np.float64)
    for start in range(0, len(movie), chunk_frames):
        block = movie[start:start + chunk_frames]
        if not np.isfinite(block).all():
            raise ValueError("movie: nonfinite pixel values")
        for roi, mask in enumerate(masks):
            result[roi, start:start + len(block)] = np.mean(block[:, mask], axis=1, dtype=np.float64)
    return result


def delta_f_over_f(traces, percentile=20.0, min_baseline=1e-6):
    """Global per-ROI percentile baseline: (F - F0) / F0. Returns (dff, F0)."""
    traces = numeric_array(traces, 2, "traces", min_time=3)
    if not np.isfinite(percentile) or not 0 <= percentile <= 100:
        raise ValueError("percentile: expected 0..100")
    if not np.isfinite(min_baseline) or min_baseline <= 0:
        raise ValueError("min_baseline: positive finite value required")
    baseline = np.percentile(traces, percentile, axis=1, keepdims=True)
    if np.any(baseline <= min_baseline):
        raise ValueError("baseline is nonpositive or too small; review offset/background correction")
    dff = (traces - baseline) / baseline
    if not np.isfinite(dff).all():
        raise ValueError("dff overflow; check input scale")
    return dff, baseline[:, 0]


def pearson_connectivity(traces):
    """Descriptive Pearson correlations only; no causal or significance inference."""
    traces = numeric_array(traces, 2, "traces", min_time=3)
    if traces.shape[0] < 2 or np.any(np.std(traces, axis=1) == 0):
        raise ValueError("correlation requires at least two nonconstant traces")
    result = np.corrcoef(traces)
    if not np.isfinite(result).all():
        raise ValueError("unstable correlation; inspect numerical scale")
    return result


def trace_qc(traces):
    traces = numeric_array(traces, 2, "traces", min_time=3)
    sd = np.std(traces, axis=1)
    return {"n_rois": int(len(traces)), "n_timepoints": int(traces.shape[1]),
            "constant_roi_indices": np.flatnonzero(sd == 0).tolist(),
            "mean": traces.mean(axis=1).tolist(), "std": sd.tolist(),
            "minimum": traces.min(axis=1).tolist(), "maximum": traces.max(axis=1).tolist()}
