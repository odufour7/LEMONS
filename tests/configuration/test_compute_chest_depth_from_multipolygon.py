"""
Unit tests for the compute_chest_depth_from_multipolygon function.

Tests cover:
    - Simple MultiPolygon with known vertical depth
    - MultiPolygon with two separated polygons
    - Degenerate case: all points on a horizontal line (depth zero)
    - Non-MultiPolygon input (error)
    - Centroid shift invariance
    - Irregular shape with known max vertical distance at similar x
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

import numpy as np
import pytest
from shapely.geometry import MultiPolygon, Polygon

from configuration.utils.functions import compute_chest_depth_from_multipolygon


def test_simple_vertical_rectangle() -> None:
    """Test a single rectangle MultiPolygon where the chest depth is the rectangle's height."""
    rect = Polygon([(0, 0), (2, 0), (2, 5), (0, 5)])
    mp = MultiPolygon([rect])
    depth = compute_chest_depth_from_multipolygon(mp)
    assert np.isclose(depth, 5.0, atol=1e-6)


def test_two_rectangles_same_x() -> None:
    """Test two rectangles stacked vertically, depth should be distance between farthest points at same x."""
    rect1 = Polygon([(0, 0), (2, 0), (2, 1), (0, 1)])
    rect2 = Polygon([(0, 5), (2, 5), (2, 6), (0, 6)])
    mp = MultiPolygon([rect1, rect2])
    depth = compute_chest_depth_from_multipolygon(mp)
    assert np.isclose(depth, 6.0, atol=1e-6)


def test_single_point_horizontal_line() -> None:
    """All points have the same y, so depth should be zero."""
    poly = Polygon([(0, 1), (1, 1), (2, 1)])
    mp = MultiPolygon([poly])
    depth = compute_chest_depth_from_multipolygon(mp)
    assert np.isclose(depth, 0.0, atol=1e-6)


def test_non_multipolygon_input() -> None:
    """Should raise ValueError for non-MultiPolygon input."""
    poly = Polygon([(0, 0), (1, 0), (1, 1)])
    with pytest.raises(ValueError):
        compute_chest_depth_from_multipolygon(poly)


def test_depth_includes_centroid_shift() -> None:
    """Test that centroid shift (with respect to the Polygon of the first test) does not affect the result."""
    rect = Polygon([(10, 10), (12, 10), (12, 15), (10, 15)])
    mp = MultiPolygon([rect])
    depth = compute_chest_depth_from_multipolygon(mp)
    assert np.isclose(depth, 5.0, atol=1e-6)


def test_irregular_shape() -> None:
    """Test an irregular polygon where the max vertical distance is not between endpoints."""
    poly = Polygon([(0, 0), (1, 2), (2, 0), (1, -2)])
    mp = MultiPolygon([poly])
    depth = compute_chest_depth_from_multipolygon(mp)
    assert np.isclose(depth, 4.0, atol=1e-6)
    assert np.isclose(depth, 4.0, atol=1e-6)
    assert np.isclose(depth, 4.0, atol=1e-6)
