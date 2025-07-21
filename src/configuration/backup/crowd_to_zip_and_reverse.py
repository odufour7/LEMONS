"""Contains functions to export crowd data to a ZIP file and save it."""

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

import io
import zipfile
from pathlib import Path

import configuration.backup.crowd_to_dict as to_dict
import configuration.backup.dict_to_xml_and_reverse as dict_to_xml
from configuration.models.crowd import Crowd


def write_crowd_data_to_zip(current_crowd: Crowd) -> io.BytesIO:
    """
    Generate an in-memory ZIP file containing XML representations of the nested dictionaries that summarize the crowd parameters.

    Parameters
    ----------
    current_crowd : Crowd
        The current crowd object containing the parameters to be saved.

    Returns
    -------
    io.BytesIO
        An in-memory ZIP file containing the XML representations of crowd parameters.
    """
    # Extract static pedestrian parameters and convert to XML
    static_data_dict = to_dict.get_static_params(current_crowd)
    static_data_bytes = dict_to_xml.static_dict_to_xml(static_data_dict)

    # Extract dynamic pedestrian parameters and convert to XML
    dynamic_data_dict = to_dict.get_dynamic_params(current_crowd)
    dynamic_data_bytes = dict_to_xml.dynamic_dict_to_xml(dynamic_data_dict)

    # Extract geometry parameters and convert to XML
    geometry_data_dict = to_dict.get_geometry_params(current_crowd)
    geometry_data_bytes = dict_to_xml.geometry_dict_to_xml(geometry_data_dict)

    # Extract material parameters and convert to XML
    materials_data_dict = to_dict.get_materials_params()
    materials_data_bytes = dict_to_xml.materials_dict_to_xml(materials_data_dict)

    # Create an in-memory ZIP file
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        # Write each XML file into the ZIP archive
        zip_file.writestr("Agents.xml", static_data_bytes)
        zip_file.writestr("AgentDynamics.xml", dynamic_data_bytes)
        zip_file.writestr("Geometry.xml", geometry_data_bytes)
        zip_file.writestr("Materials.xml", materials_data_bytes)

    # Move the buffer's pointer to the beginning
    zip_buffer.seek(0)
    return zip_buffer


def save_crowd_data_to_zip(current_crowd: Crowd, output_zip_path: Path) -> None:
    """
    Save crowd data as a ZIP file containing multiple XML files.

    Parameters
    ----------
    current_crowd : Crowd
        The current crowd object containing the parameters to be saved.
    output_zip_path : Path
        The path where the ZIP file will be saved.

    Raises
    ------
    TypeError
        If `output_zip_path` is not a Path object.
    ValueError
        If `output_zip_path` does not have a .zip extension.
    """
    if not isinstance(output_zip_path, Path):
        raise TypeError("`output_zip_path` should be a Path object.")
    if not output_zip_path.suffix == ".zip":
        raise ValueError("`output_zip_path` should have a .zip extension.")

    # Ensure the output directory exists
    output_zip_path.parent.mkdir(parents=True, exist_ok=True)

    # Generate the ZIP file in memory
    zip_buffer = write_crowd_data_to_zip(current_crowd)

    # Write the in-memory ZIP file to the specified output path
    with open(output_zip_path, "wb") as output_file:
        output_file.write(zip_buffer.read())

    # Close the in-memory buffer
    zip_buffer.close()
