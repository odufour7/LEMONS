"""
Unit tests for the wrap_angle function.

Tests cover:
    - Canonical angles (0, 180, -180, 360, -360, 720, -720)
    - Angles just outside the bounds
    - Negative and positive values
    - Large and small angles
    - Floating point precision
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

from configuration.utils.functions import wrap_angle


def test_zero_angle() -> None:
    """Test that 0 degrees wraps to 0."""
    assert wrap_angle(0.0) == 0.0


def test_positive_angles() -> None:
    """Test wrapping of positive angles."""
    assert wrap_angle(45.0) == 45.0
    assert wrap_angle(180.0) == -180.0
    assert wrap_angle(181.0) == -179.0
    assert wrap_angle(359.0) == -1.0
    assert wrap_angle(360.0) == 0.0
    assert wrap_angle(540.0) == -180.0
    assert wrap_angle(720.0) == 0.0


def test_negative_angles() -> None:
    """Test wrapping of negative angles."""
    assert wrap_angle(-45.0) == -45.0
    assert wrap_angle(-180.0) == -180.0
    assert wrap_angle(-181.0) == 179.0
    assert wrap_angle(-359.0) == 1.0
    assert wrap_angle(-360.0) == 0.0
    assert wrap_angle(-540.0) == -180.0
    assert wrap_angle(-720.0) == 0.0


def test_angles_just_outside_bounds() -> None:
    """Test angles just outside the -180 and 180 bounds."""
    assert np.isclose(wrap_angle(179.9999), 179.9999, atol=1e-6)
    assert np.isclose(wrap_angle(180.0001), -179.9999, atol=1e-6)
    assert np.isclose(wrap_angle(-179.9999), -179.9999, atol=1e-6)
    assert np.isclose(wrap_angle(-180.0001), 179.9999, atol=1e-6)


def test_large_angles() -> None:
    """Test very large positive and negative angles."""
    assert wrap_angle(123456.0) == ((123456.0 + 180.0) % 360.0) - 180.0
    assert wrap_angle(-987654.0) == ((-987654.0 + 180.0) % 360.0) - 180.0


def test_floating_point_precision() -> None:
    """Test floating point precision edge case."""
    assert np.isclose(wrap_angle(180.0000001), -179.9999999, atol=1e-7)
    assert np.isclose(wrap_angle(-180.0000001), 179.9999999, atol=1e-7)
