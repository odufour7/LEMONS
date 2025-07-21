"""
Unit tests for the compute_bideltoid_breadth_from_multipolygon function.

Test cases cover:
    - Simple MultiPolygon with a known maximum horizontal breadth.
    - Centroid shift of the polygon (should not affect the breadth).
    - MultiPolygon containing two separated polygons.
    - Non-MultiPolygon input (should raise ValueError).
    - Degenerate case: all points vertically aligned (breadth zero).
    - Irregular polygon where the maximum horizontal breadth is not between endpoints.
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

from configuration.utils.functions import compute_bideltoid_breadth_from_multipolygon


def test_simple_horizontal_rectangle() -> None:
    """Test a single rectangle MultiPolygon where the breadth is the rectangle's width."""
    rect = Polygon([(0, 0), (4, 0), (4, 2), (0, 2)])
    mp = MultiPolygon([rect])
    breadth = compute_bideltoid_breadth_from_multipolygon(mp)
    assert np.isclose(breadth, 4.0, atol=1e-6)


def test_breadth_includes_centroid_shift() -> None:
    """Test that centroid shift (with respect to the Polygon of the first test) does not affect the result."""
    rect = Polygon([(10, 10), (14, 10), (14, 12), (10, 12)])
    mp = MultiPolygon([rect])
    breadth = compute_bideltoid_breadth_from_multipolygon(mp)
    assert np.isclose(breadth, 4.0, atol=1e-6)


def test_two_rectangles_same_y() -> None:
    """Test two rectangles side by side, breadth should be distance between farthest points at same y."""
    rect1 = Polygon([(0, 0), (2, 0), (2, 1), (0, 1)])
    rect2 = Polygon([(5, 0), (7, 0), (7, 1), (5, 1)])
    mp = MultiPolygon([rect1, rect2])
    breadth = compute_bideltoid_breadth_from_multipolygon(mp)
    assert np.isclose(breadth, 7.0, atol=1e-6)


def test_single_point_vertical_line() -> None:
    """All points have the same x, so breadth should be zero."""
    poly = Polygon([(1, 0), (1, 1), (1, 2)])
    mp = MultiPolygon([poly])
    breadth = compute_bideltoid_breadth_from_multipolygon(mp)
    assert np.isclose(breadth, 0.0, atol=1e-6)


def test_non_multipolygon_input() -> None:
    """Should raise ValueError for non-MultiPolygon input."""
    poly = Polygon([(0, 0), (1, 0), (1, 1)])
    with pytest.raises(ValueError):
        compute_bideltoid_breadth_from_multipolygon(poly)


def test_irregular_shape() -> None:
    """Test an irregular polygon where the max horizontal distance is not between endpoints."""
    poly = Polygon([(0, 0), (2, 1), (1, 2), (0, 1)])
    mp = MultiPolygon([poly])
    breadth = compute_bideltoid_breadth_from_multipolygon(mp)
    assert np.isclose(breadth, 2.0, atol=1e-6)
    assert np.isclose(breadth, 2.0, atol=1e-6)
    assert np.isclose(breadth, 2.0, atol=1e-6)
    assert np.isclose(breadth, 2.0, atol=1e-6)
    assert np.isclose(breadth, 2.0, atol=1e-6)
    assert np.isclose(breadth, 2.0, atol=1e-6)
    assert np.isclose(breadth, 2.0, atol=1e-6)
