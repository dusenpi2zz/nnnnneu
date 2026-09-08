import numpy as np
import pytest

from neuro_methods.signals import delta_f_over_f, extract_roi_traces, pearson_connectivity


def test_roi_means_against_hand_calculation():
    movie = np.array([[[1, 3], [10, 20]], [[2, 6], [20, 40]], [[3, 9], [30, 60]]])
    masks = np.array([[[1, 1], [0, 0]], [[0, 0], [1, 1]]])
    expected = [[2, 4, 6], [15, 30, 45]]
    for chunk in [1, 2, 100]:
        np.testing.assert_allclose(extract_roi_traces(movie, masks, chunk), expected)


@pytest.mark.parametrize("masks", [np.zeros((1, 2, 2)), np.ones((2, 2, 2)),
                                     np.full((1, 2, 2), .5), np.ones((1, 3, 2))])
def test_rejects_empty_overlapping_soft_or_misaligned_masks(masks):
    with pytest.raises(ValueError):
        extract_roi_traces(np.ones((3, 2, 2)), masks)


def test_dff_matches_defined_baseline():
    dff, baseline = delta_f_over_f([[10, 20, 30], [2, 4, 6]], percentile=0)
    np.testing.assert_allclose(baseline, [10, 2])
    np.testing.assert_allclose(dff, [[0, 1, 2], [0, 1, 2]])


@pytest.mark.parametrize("traces", [[[0, 1, 2]], [[-2, -1, 0]], [[1, np.nan, 3]],
                                      [[1, 2]], [[1+1j, 2, 3]]])
def test_invalid_fluorescence_rejected(traces):
    with pytest.raises(ValueError):
        delta_f_over_f(traces, percentile=0)


def test_pearson_positive_negative_affine_invariance():
    corr = pearson_connectivity([[1, 2, 3, 4], [12, 14, 16, 18], [4, 3, 2, 1]])
    np.testing.assert_allclose(corr, [[1, 1, -1], [1, 1, -1], [-1, -1, 1]], atol=1e-14)


@pytest.mark.parametrize("traces", [[[1, 1, 1], [1, 2, 3]], [[1, 2, 3]], [[1, 2], [3, 4]]])
def test_invalid_correlation_rejected(traces):
    with pytest.raises(ValueError):
        pearson_connectivity(traces)
