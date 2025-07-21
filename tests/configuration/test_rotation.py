"""
Unit tests for Agent rotation.

Tests cover:
    - Initial orientation state validation
    - 2D shape positioning accuracy during rotation
    - 2D 3D centroid position invariance under rotation
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

import configuration.utils.constants as cst
from configuration.models.agents import Agent
from configuration.models.measures import AgentMeasures
from configuration.utils.typing_custom import Sex


@pytest.fixture
def agent() -> Agent:
    """
    Fixture to create an Agent instance for testing.

    Returns
    -------
    Agent
        An instance of Agent with predefined type and measures.
    """
    agent_type = cst.AgentTypes.pedestrian
    measures: dict[str, Sex | float] = {
        "sex": "male",
        "bideltoid_breadth": 45.0,
        "chest_depth": 25.0,
        "height": 180.0,
        "weight": 75.0,
    }
    agent_measures = AgentMeasures(agent_type=agent_type, measures=measures)
    return Agent(agent_type=agent_type, measures=agent_measures)


def test_initial_orientation(agent: Agent) -> None:
    """
    Test that the initial orientation of the agent is 90 degrees.

    Parameters
    ----------
    agent : Agent
        The agent fixture.
    """
    orientation = agent.get_agent_orientation()
    assert orientation == 0.0, f"Expected orientation 0.0, got {orientation}"


def test_shapes2d_center_y(agent: Agent) -> None:
    """
    Test that the y-coordinates of each 2D shape center are close to 0.0.

    Parameters
    ----------
    agent : Agent
        The agent fixture.
    """
    for shape_dict in agent.shapes2D.get_additional_parameters().values():
        assert abs(shape_dict["x"]) < 0.05, f"Shape center y-coordinate is not close to 0.0: {shape_dict['x']}"


def test_rotation_and_shapes2d_center_x(agent: Agent) -> None:
    """
    Test that after rotating the agent by -90°, the orientation is -90 and the x-coordinates of each 2D shape center are close to -90.

    Parameters
    ----------
    agent : Agent
        The agent fixture.
    """
    agent.rotate(-90)
    orientation = agent.get_agent_orientation()
    assert orientation == -90.0, f"Expected orientation -90.0 after rotation, got {orientation}"
    for shape_dict in agent.shapes2D.get_additional_parameters().values():
        assert abs(shape_dict["y"]) < 0.05, f"Shape center x-coordinate is not close to -90.0: {shape_dict['y']}"


def test_center_of_mass_invariance_on_rotation(agent: Agent) -> None:
    """
    Test that the center of mass does not change after rotation.

    Parameters
    ----------
    agent : Agent
        The agent fixture.
    """
    initial_position = agent.get_position()
    agent.rotate(-90)
    final_position = agent.get_position()
    assert np.isclose(initial_position.x, final_position.x, atol=0.05), "The center of mass x should not change after rotation."
    assert np.isclose(initial_position.y, final_position.y, atol=0.05), "The center of mass y should not change after rotation."
    agent.rotate(380)
    final_position = agent.get_position()
    assert np.isclose(initial_position.x, final_position.x, atol=0.05), "The center of mass x should not change after rotation."
    assert np.isclose(initial_position.y, final_position.y, atol=0.05), "The center of mass y should not change after rotation."
    agent.rotate(-400)
    final_position = agent.get_position()
    assert np.isclose(initial_position.x, final_position.x, atol=0.05), "The center of mass x should not change after rotation."
    assert np.isclose(initial_position.y, final_position.y, atol=0.05), "The center of mass y should not change after rotation."


def test_centroid_body3d_invariance_on_rotation(agent: Agent) -> None:
    """
    Test that the 3D centroid of the body does not change after rotation.

    Parameters
    ----------
    agent : Agent
        The agent fixture.
    """
    initial_centroid = agent.get_centroid_body3D()
    agent.rotate_body3D(-90)
    final_centroid = agent.get_centroid_body3D()
    assert np.isclose(initial_centroid.x, final_centroid.x, atol=0.05), "The centroid body x should not change after rotation."
    assert np.isclose(initial_centroid.y, final_centroid.y, atol=0.05), "The centroid body y should not change after rotation."
    agent.rotate_body3D(380)
    final_centroid = agent.get_centroid_body3D()
    assert np.isclose(initial_centroid.x, final_centroid.x, atol=0.05), "The centroid body x should not change after rotation."
    assert np.isclose(initial_centroid.y, final_centroid.y, atol=0.05), "The centroid body y should not change after rotation."
