"""
Unit tests for the rotate_vectors function.

Tests cover:
    - Rotation accuracy for standard angles (0°, 90°, 180°, 270°)
    - Non-integer and negative angle values
    - Empty dictionary handling
    - Multiple vector transformations in single operation
    - Input immutability verification
    - Error handling for invalid vector formats
"""

# Copyright  2025  Institute of Light and Matter, CNRS UMR 5306, University Claude Bernard Lyon 1
# Contributors: Oscar DUFOUR, Maxime STAPELLE, Alexandre NICOLAS

# This software is a computer program designed to generate a realistic crowd from anthropometric data and
# simulate the mechanical interactions that occur within it and with obstacles.

# This software is governed by the CeCILL-B license under French law and abiding by the rules of distribution
# of free software.  You can  use, modify and/ or redistribute the software under the terms of the CeCILL-B
# license as circulated by CEA, CNRS and INRIA at the following URL "http://www.cecill.info".

# As a counterpart to the access to the source code and  rights to copy, modify and redistribute granted by
# the license, users are provided only with a limited warranty  and the software's author,  the holder of the
# economic rights,  and the successive licensors  have only  limited liability.

# In this respect, the user's attention is drawn to the risks associated with loading,  using,  modifying
# and/or developing or reproducing the software by the user in light of its specific status of free software,
# that may mean  that it is complicated to manipulate,  and  that  also therefore means  that it is reserved
# for developers  and  experienced professionals having in-depth computer knowledge. Users are therefore
# encouraged to load and test the software's suitability as regards their requirements in conditions enabling
# the security of their systems and/or data to be ensured and,  more generally, to use and operate it in the
# same conditions as regards security.

# The fact that you are presently reading this means that you have had knowledge of the CeCILL-B license and that
# you accept its terms.

import math

import pytest

from configuration.utils.functions import rotate_vectors


def vectors_close(vec1: tuple[float, float], vec2: tuple[float, float], tol: float = 1e-8) -> bool:
    """
    Help function to compare two 2D vectors for approximate equality.

    Parameters
    ----------
    vec1 : tuple[float, float]
        First vector to compare.
    vec2 : tuple[float, float]
        Second vector to compare.
    tol : float
        Tolerance for comparison.

    Returns
    -------
    bool
        True if the vectors are approximately equal, False otherwise.
    """
    return math.isclose(vec1[0], vec2[0], abs_tol=tol) and math.isclose(vec1[1], vec2[1], abs_tol=tol)


def test_rotate_0_degrees() -> None:
    """Test rotation by 0 degrees (should return original vectors)."""
    vectors = {"a": (1.0, 0.0), "b": (0.0, 1.0)}
    result = rotate_vectors(vectors, 0)
    for k, v in vectors.items():
        assert vectors_close(result[k], v)


def test_rotate_90_degrees() -> None:
    """Test rotation by 90 degrees."""
    vectors = {"x": (1.0, 0.0), "y": (0.0, 1.0)}
    expected = {"x": (0.0, 1.0), "y": (-1.0, 0.0)}
    result = rotate_vectors(vectors, 90)
    for k in vectors:
        assert vectors_close(result[k], expected[k])


def test_rotate_180_degrees() -> None:
    """Test rotation by 180 degrees."""
    vectors = {"v": (1.0, 0.0), "w": (0.0, 1.0)}
    expected = {"v": (-1.0, 0.0), "w": (0.0, -1.0)}
    result = rotate_vectors(vectors, 180)
    for k in vectors:
        assert vectors_close(result[k], expected[k])


def test_rotate_270_degrees() -> None:
    """Test rotation by 270 degrees (or -90 degrees)."""
    vectors = {"p": (1.0, 0.0), "q": (0.0, 1.0)}
    expected = {"p": (0.0, -1.0), "q": (1.0, 0.0)}
    result = rotate_vectors(vectors, 270)
    for k in vectors:
        assert vectors_close(result[k], expected[k])


def test_rotate_negative_angle() -> None:
    """Test rotation by a negative angle."""
    vectors = {"a": (1.0, 0.0)}
    theta = -90
    expected = {"a": (0.0, -1.0)}
    result = rotate_vectors(vectors, theta)
    assert vectors_close(result["a"], expected["a"])


def test_rotate_non_integer_angle() -> None:
    """Test rotation by a non-integer angle."""
    vectors = {"a": (1.0, 0.0)}
    theta = 45.5
    expected_x = math.cos(math.radians(theta))
    expected_y = math.sin(math.radians(theta))
    result = rotate_vectors(vectors, theta)
    assert math.isclose(result["a"][0], expected_x, abs_tol=1e-8)
    assert math.isclose(result["a"][1], expected_y, abs_tol=1e-8)


def test_rotate_empty_dict() -> None:
    """Test rotating an empty dictionary."""
    assert not rotate_vectors({}, 45)


def test_multiple_vectors() -> None:
    """Test rotating multiple vectors."""
    vectors = {"a": (1.0, 0.0), "b": (0.0, 1.0), "c": (1.0, 1.0), "d": (-1.0, -1.0)}
    theta = 90
    expected = {"a": (0.0, 1.0), "b": (-1.0, 0.0), "c": (-1.0, 1.0), "d": (1.0, -1.0)}
    result = rotate_vectors(vectors, theta)
    for k in vectors:
        assert vectors_close(result[k], expected[k])


def test_input_not_modified() -> None:
    """Test that input dictionary is not modified in place."""
    vectors = {"a": (1.0, 0.0)}
    vectors_copy = dict(vectors)
    rotate_vectors(vectors, 90)
    assert vectors == vectors_copy


def test_invalid_vector_format() -> None:
    """Test that invalid vector format (not a tuple of two floats) raises an error."""
    vectors = {"bad": (1.0,)}
    with pytest.raises(ValueError):
        rotate_vectors(vectors, 90)
