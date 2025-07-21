"""Test the loading and saving of boundaries parameters in XML format."""

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

from pathlib import Path

import pytest
from _pytest.fixtures import SubRequest

import configuration.backup.dict_to_xml_and_reverse as fun_xml
from configuration.utils.typing_custom import GeometryDataType


@pytest.fixture
def boundaries_dict_two_walls() -> GeometryDataType:
    """
    Provide a fixture containing boundary data for a geometry with two walls.

    Returns
    -------
    GeometryDataType
        A dictionary representing the geometry data, including dimensions and
        wall properties such as material ID and corner coordinates.
    """
    return {
        "Geometry": {
            "Dimensions": {"Lx": 6.08, "Ly": 5.08},
            "Wall": {
                "Wall0": {
                    "Id": 0,
                    "MaterialId": "concrete",
                    "Corners": {
                        "Corner0": {"Coordinates": (0.0, 0.0)},
                        "Corner1": {"Coordinates": (0.0, 0.0)},
                        "Corner2": {"Coordinates": (0.0, 0.0)},
                        "Corner3": {"Coordinates": (0.0, 0.0)},
                        "Corner4": {"Coordinates": (0.0, 0.0)},
                    },
                },
                "Wall1": {
                    "Id": 1,
                    "MaterialId": "human_naked",
                    "Corners": {
                        "Corner0": {"Coordinates": (0.0, 0.0)},
                        "Corner1": {"Coordinates": (0.0, 0.0)},
                        "Corner2": {"Coordinates": (0.0, 0.0)},
                        "Corner3": {"Coordinates": (0.0, 0.0)},
                        "Corner4": {"Coordinates": (0.0, 0.0)},
                    },
                },
            },
        },
    }


@pytest.fixture
def boundaries_dict_one_wall() -> GeometryDataType:
    """
    Provide a fixture containing boundary data for a geometry with one wall.

    Returns
    -------
    GeometryDataType
        A dictionary representing the geometry data, including dimensions and
        wall properties such as material ID and corner coordinates.
    """
    return {
        "Geometry": {
            "Dimensions": {"Lx": 6.08, "Ly": 5.08},
            "Wall": {
                "Wall0": {
                    "Id": 0,
                    "MaterialId": "human_clothes",
                    "Corners": {
                        "Corner0": {"Coordinates": (0.0, 0.0)},
                        "Corner1": {"Coordinates": (0.0, 0.0)},
                        "Corner2": {"Coordinates": (0.0, 0.0)},
                        "Corner3": {"Coordinates": (0.0, 0.0)},
                        "Corner4": {"Coordinates": (0.0, 0.0)},
                    },
                },
            },
        },
    }


@pytest.mark.parametrize(
    "boundaries_dict",
    [
        "boundaries_dict_two_walls",
        "boundaries_dict_one_wall",
    ],
)
def test_geometry_dict_to_xml_and_back(boundaries_dict: GeometryDataType, tmp_path: Path, request: SubRequest) -> None:
    """
    Test the loading and saving of boundaries parameters in XML format.

    Parameters
    ----------
    boundaries_dict : GeometryDataType
        A dictionary representing the geometry data, including dimensions and
        wall properties such as material ID and corner coordinates.
    tmp_path : Path
        Temporary directory for XML file storage.
    request : SubRequest
        The pytest request object used to access fixtures.
    """
    # Get the fixture data
    boundaries_dict = request.getfixturevalue(boundaries_dict)

    # Convert dictionary to XML
    xml_data = fun_xml.geometry_dict_to_xml(boundaries_dict)

    # Save XML to a temporary file
    temp_file_path = tmp_path / "output_boundaries.xml"
    with open(temp_file_path, "wb") as file:
        file.write(xml_data)

    # Read back the XML file and convert it back to a dictionary
    with open(temp_file_path, "r", encoding="utf-8") as file:
        loaded_xml_data = file.read()

    # Parse the XML string back to a dictionary
    parsed_boundaries = fun_xml.geometry_xml_to_dict(loaded_xml_data)

    # Assert that the original dictionary matches the parsed dictionary
    assert boundaries_dict == parsed_boundaries
    assert boundaries_dict == parsed_boundaries
