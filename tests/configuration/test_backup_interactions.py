"""Test the loading and saving of interactions parameters in XML format."""

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

import configuration.backup.crowd_to_dict as fun_dict
import configuration.backup.dict_to_xml_and_reverse as fun_xml
from configuration.models.crowd import Crowd


@pytest.fixture
def crowd(request: pytest.FixtureRequest) -> Crowd:
    """
    Fixture creating Crowd instances with parameterized agent counts and packing states.

    Parameters
    ----------
    request : pytest.FixtureRequest
        Contains tuple of (agent_count, should_pack) parameters.

    Returns
    -------
    Crowd
        Configured instance with agents and optional force packing.
    """
    agent_count, should_pack = request.param
    c = Crowd()
    c.create_agents(number_agents=agent_count)

    if should_pack:
        c.pack_agents_with_forces()

    return c


@pytest.mark.parametrize(
    "crowd", [(1, True), (1, False), (3, True), (3, False)], indirect=True, ids=["1_packed", "1_unpacked", "3_packed", "3_unpacked"]
)
def test_interactions_dict_xml_roundtrip(crowd: Crowd, tmp_path: Path) -> None:
    """
    Test the loading and saving of interactions parameters in XML format.

    There are 4 scenarios:
        - 1 agent (packed/unpacked)
        - 3 agents (packed/unpacked)

    Parameters
    ----------
    crowd : Crowd
        The crowd fixture with agents and optional packing.
    tmp_path : Path
        Temporary directory for XML file storage.
    """
    # Original test logic remains unchanged
    interactions_dict = fun_dict.get_interactions_params(crowd)
    interactions_bytes = fun_xml.interactions_dict_to_xml(interactions_dict)

    xml_file = tmp_path / "test_interactions.xml"
    xml_file.write_bytes(interactions_bytes)

    content = xml_file.read_bytes()
    interactions_dict_new = fun_xml.interactions_xml_to_dict(content)

    assert interactions_dict_new == interactions_dict, (
        f"Data mismatch for {len(crowd.agents)} agents {'packed' if hasattr(crowd, 'packed_forces') else 'unpacked'}"
    )
