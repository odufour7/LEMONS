"""
Unit tests for the from_string_to_tuple function.

Tests cover:
    - Valid string inputs (with and without parentheses, extra spaces, negative numbers, scientific notation)
    - Handling of leading/trailing whitespace
    - Invalid inputs (non-string, wrong number of elements, non-numeric values, empty string)
    - Error message validation for incorrect formats
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

import pytest

from configuration.utils.functions import from_string_to_tuple


def test_valid_input_no_parentheses() -> None:
    """Test valid input without parentheses."""
    assert from_string_to_tuple("1.0, 2.0") == (1.0, 2.0)


def test_valid_input_with_parentheses() -> None:
    """Test valid input with parentheses."""
    assert from_string_to_tuple("(3.14, 2.72)") == (3.14, 2.72)


def test_valid_input_with_spaces() -> None:
    """Test valid input with extra spaces."""
    assert from_string_to_tuple("  4.0 ,   5.0 ") == (4.0, 5.0)


def test_valid_input_negative_numbers() -> None:
    """Test valid input with negative numbers."""
    assert from_string_to_tuple(" -1.5, -2.5 ") == (-1.5, -2.5)


def test_valid_input_scientific_notation() -> None:
    """Test valid input with scientific notation."""
    assert from_string_to_tuple("1e3, 2e-2") == (1000.0, 0.02)


def test_invalid_input_not_a_string() -> None:
    """Test that non-string input raises ValueError."""
    with pytest.raises(ValueError, match="Input must be a string."):
        from_string_to_tuple(123)


def test_invalid_input_wrong_number_of_elements() -> None:
    """Test that input with wrong number of elements raises ValueError."""
    with pytest.raises(ValueError, match="`string` must contain exactly two numbers separated by a comma."):
        from_string_to_tuple("1.0, 2.0, 3.0")

    with pytest.raises(ValueError, match="`string` must contain exactly two numbers separated by a comma."):
        from_string_to_tuple("1.0")


def test_invalid_input_non_numeric() -> None:
    """Test that non-numeric elements raise ValueError."""
    with pytest.raises(ValueError, match="Both elements must be convertible to float."):
        from_string_to_tuple("a, b")

    with pytest.raises(ValueError, match="Both elements must be convertible to float."):
        from_string_to_tuple("(1.0, b)")


def test_invalid_input_empty_string() -> None:
    """Test that empty string raises ValueError."""
    with pytest.raises(ValueError):
        from_string_to_tuple("")


def test_valid_input_trailing_comma_spaces() -> None:
    """Test input with trailing and leading whitespace and parentheses."""
    assert from_string_to_tuple(" (  6.0 ,  7.0 ) ") == (6.0, 7.0)
