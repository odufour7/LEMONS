"""Test the loading and saving of dynamic parameters in XML format."""

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
from configuration.utils.typing_custom import DynamicCrowdDataType


@pytest.fixture
def dynamical_parameters_crowd() -> DynamicCrowdDataType:
    """
    Fixture to provide dynamic parameters for the crowd.

    Returns
    -------
    DynamicCrowdDataType
        A dictionary containing dynamic parameters for two agents.
    """
    return {
        "Agents": {
            "Agent0": {
                "Id": 0,
                "Kinematics": {
                    "Position": (1.98, 0.96),
                    "Velocity": (0.0, 0.0),
                    "Theta": 0.52,
                    "Omega": 0,
                },
                "Dynamics": {
                    "Fp": (55.74, 225.83),
                    "Mp": 0.49,
                },
            },
            "Agent1": {
                "Id": 1,
                "Kinematics": {
                    "Position": (2.68, 0.98),
                    "Velocity": (0.0, 0.0),
                    "Theta": -0.23,
                    "Omega": 0,
                },
                "Dynamics": {
                    "Fp": (52.47, 187.62),
                    "Mp": -0.02,
                },
            },
        }
    }


@pytest.mark.parametrize(
    "dynamical_parameters_crowd_dict",
    ["dynamical_parameters_crowd"],
)
def test_dynamic_parameters_dict_to_xml_and_back(
    dynamical_parameters_crowd_dict: DynamicCrowdDataType, tmp_path: Path, request: SubRequest
) -> None:
    """
    Test the loading and saving of dynamic parameters in XML format.

    This test converts a dictionary to XML, saves it to a temporary file, reads it back, and ensures
    that the parsed dictionary matches the original.

    Parameters
    ----------
    dynamical_parameters_crowd_dict : DynamicCrowdDataType
        A dictionary containing dynamic parameters for two agents.
    tmp_path : Path
        Temporary directory for XML file storage.
    request : SubRequest
        The pytest request object used to access fixtures.
    """
    # Get the fixture data
    dynamical_parameters_crowd_dict = request.getfixturevalue(dynamical_parameters_crowd_dict)

    # Convert the dictionary to XML format
    xml_data = fun_xml.dynamic_dict_to_xml(dynamical_parameters_crowd_dict)

    # Save XML to a temporary file
    temp_file_path = tmp_path / "output_dynamic_crowd.xml"
    with open(temp_file_path, "wb") as file:
        file.write(xml_data)

    # Read back the XML file and convert it back to a dictionary
    with open(temp_file_path, "r", encoding="utf-8") as file:
        loaded_xml_data = file.read()

    # Parse the XML string back into a dictionary
    parsed_data = fun_xml.dynamic_xml_to_dict(loaded_xml_data)

    # Assert that the parsed dictionary matches the original one
    assert parsed_data == dynamical_parameters_crowd_dict, "Parsed data does not match original data."
