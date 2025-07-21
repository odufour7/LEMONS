"""
Unit tests for the compute_moment_of_inertia function.

Tests cover:
    - Correct computation for simple polygons (square)
    - Handling of MultiPolygon geometries
    - Zero and negative weight values
    - Invalid geometry type validation
    - Area scaling consistency
    - Mass distribution in composite geometries
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
from shapely.geometry import MultiPolygon, Polygon

from configuration.utils.functions import compute_moment_of_inertia


def test_square_polygon() -> None:
    """Test moment of inertia for a unit square at origin."""
    square = Polygon([(0, 0), (1, 0), (1, 1), (0, 1)])  # cm
    weight = 2.0
    result = compute_moment_of_inertia(square, weight)
    # Analytical: I = (m/6) for unit square about centroid (converted to kg·m² as per function)
    expected = (weight / 6.0) * 1e-4
    print(f"Square moment of inertia: {result}, expected: {expected}")
    assert math.isclose(result, expected, rel_tol=1e-6)


def test_multipolygon_sum() -> None:
    """Test that MultiPolygon sums the moments of the components."""
    poly1 = Polygon([(0, 0), (1, 0), (1, 1), (0, 1)])
    poly2 = Polygon([(2, 0), (3, 0), (3, 1), (2, 1)])
    mp = MultiPolygon([poly1, poly2])
    weight = 4.0
    # Should be the same as two squares, each with half the weight
    expected = compute_moment_of_inertia(poly1, weight / 2) + compute_moment_of_inertia(poly2, weight / 2)
    result = compute_moment_of_inertia(mp, weight)
    assert math.isclose(result, expected, rel_tol=1e-8)


def test_zero_weight() -> None:
    """Test that zero weight returns zero moment."""
    square = Polygon([(0, 0), (1, 0), (1, 1), (0, 1)])
    assert compute_moment_of_inertia(square, 0.0) == 0.0


def test_negative_weight() -> None:
    """Test that negative weight returns negative moment."""
    square = Polygon([(0, 0), (1, 0), (1, 1), (0, 1)])
    result = compute_moment_of_inertia(square, -2.0)
    assert result < 0


def test_invalid_geometry_type() -> None:
    """Test that invalid geometry raises TypeError."""
    with pytest.raises(TypeError):
        compute_moment_of_inertia("not_a_polygon", 1.0)


def test_scaling_with_area() -> None:
    """Test that scaling the polygon scales the moment of inertia by area^2."""
    square = Polygon([(0, 0), (1, 0), (1, 1), (0, 1)])
    weight = 2.0
    I1 = compute_moment_of_inertia(square, weight)
    # If distance scaled by 2, mass scaled by 4 then inertia should be scaled by 16 (since inertia ~ mass * r^2)
    square2 = Polygon([(0, 0), (2, 0), (2, 2), (0, 2)])
    I2 = compute_moment_of_inertia(square2, weight * 4)
    assert math.isclose(I2, I1 * 16, rel_tol=1e-6)
