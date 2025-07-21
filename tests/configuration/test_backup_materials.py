"""Test the loading and saving of material parameters in XML format."""

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
from configuration.utils.typing_custom import MaterialsDataType


@pytest.fixture
def materials_dict() -> MaterialsDataType:
    """
    Fixture to provide material parameters for testing.

    Returns
    -------
    MaterialsDataType
        A dictionary containing material parameters, including intrinsic properties
        and binary contact properties between different materials.
    """
    return {
        "Materials": {
            "Intrinsic": {
                "Material0": {"Id": "Steel", "YoungModulus": 68.0, "ShearModulus": 25.5},
                "Material1": {"Id": "Aluminum", "YoungModulus": 200.0, "ShearModulus": 79.3},
                "Material2": {"Id": "Copper", "YoungModulus": 116, "ShearModulus": 41.4},
            },
            "Binary": {
                "Contact0": {
                    "Id1": "Steel",
                    "Id2": "Aluminum",
                    "GammaNormal": 1.3 * 10**4,
                    "GammaTangential": 1.3 * 10**4,
                    "KineticFriction": 0.5,
                },
                "Contact1": {
                    "Id1": "Steel",
                    "Id2": "Copper",
                    "GammaNormal": 1.3 * 10**4,
                    "GammaTangential": 1.3 * 10**4,
                    "KineticFriction": 0.5,
                },
                "Contact2": {
                    "Id1": "Aluminum",
                    "Id2": "Copper",
                    "GammaNormal": 1.3 * 10**4,
                    "GammaTangential": 1.3 * 10**4,
                    "KineticFriction": 0.5,
                },
                "Contact3": {
                    "Id1": "Aluminum",
                    "Id2": "Aluminum",
                    "GammaNormal": 1.3 * 10**4,
                    "GammaTangential": 1.3 * 10**4,
                    "KineticFriction": 0.5,
                },
                "Contact4": {
                    "Id1": "Copper",
                    "Id2": "Copper",
                    "GammaNormal": 1.3 * 10**4,
                    "GammaTangential": 1.3 * 10**4,
                    "KineticFriction": 0.5,
                },
                "Contact5": {
                    "Id1": "Steel",
                    "Id2": "Steel",
                    "GammaNormal": 1.3 * 10**4,
                    "GammaTangential": 1.3 * 10**4,
                    "KineticFriction": 0.5,
                },
            },
        }
    }


@pytest.mark.parametrize(
    "materials_dict_fixture",
    ["materials_dict"],
)
def test_materials_dict_to_xml_and_back(materials_dict_fixture: MaterialsDataType, tmp_path: Path, request: SubRequest) -> None:
    """
    Test the loading and saving of material parameters in XML format.

    This test converts a dictionary to XML, saves it to a temporary file, reads it back,
    and ensures that the parsed dictionary matches the original.

    Parameters
    ----------
    materials_dict_fixture : MaterialsDataType
        A fixture containing material parameters for testing.
    tmp_path : Path
        A temporary directory provided by pytest for file operations.
    request : SubRequest
        The pytest request object used to access fixtures.
    """
    # Get the fixture data
    materials_dict_fixture = request.getfixturevalue(materials_dict_fixture)

    # Convert the dictionary to XML format
    xml_data = fun_xml.materials_dict_to_xml(materials_dict_fixture)

    # Save XML to a temporary file
    temp_file_path = tmp_path / "output_materials.xml"
    with open(temp_file_path, "wb") as file:
        file.write(xml_data)

    # Read back the XML file and convert it back to a dictionary
    with open(temp_file_path, "r", encoding="utf-8") as file:
        loaded_xml_data = file.read()

    # Parse the XML string back into a dictionary
    parsed_data = fun_xml.materials_xml_to_dict(loaded_xml_data)

    # Assert that the parsed dictionary matches the original one
    assert parsed_data == materials_dict_fixture, (
        f"Parsed data does not match original data.\nExpected: {materials_dict_fixture}\nGot: {parsed_data}"
    )
