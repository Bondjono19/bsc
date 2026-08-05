import numpy as np
from recognition.utils.get_points import get_reference_points


def test_reference_points_shape_and_dtype():
    points = get_reference_points()
    assert points.shape == (5, 2)
    assert points.dtype == np.float32


def test_reference_points_reshape_to_5x2():
    # RecognitionService reshapes these into (5, 2) landmark coordinates.
    points = np.asarray(get_reference_points(), dtype=np.float32).reshape(5, 2)
    assert points.shape == (5, 2)


def test_reference_points_are_within_112_crop():
    # Points map onto a 112x112 aligned face crop.
    points = get_reference_points()
    assert np.all(points >= 0)
    assert np.all(points <= 112)
