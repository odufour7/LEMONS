"""
Unit tests for Agent translation mechanics across dimensional spaces.

Tests cover:
    - Agent's initial position is set correctly
    - Agent's position is correctly updated after translation of the 2D shapes in x and y directions
    - Agent's 3D body centroid is correctly updated after translation in x and y directions
    - Agent's 3D body centroid and lowest height are correctly updated after translation in z direction
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


def test_initial_position(agent: Agent) -> None:
    """
    Test that the agent's initial position is set correctly.

    Parameters
    ----------
    agent : Agent
        The agent fixture.
    """
    initial_position = agent.get_position()
    initial_lowest_altitude = min(agent.shapes3D.shapes.keys())
    assert abs(initial_position.x) < 0.05, "The x-coordinate should be initialized to 0.0."
    assert abs(initial_position.y) < 0.05, "The y-coordinate should be initialized to 0.0."
    assert abs(initial_lowest_altitude) < 0.05, "The z-coordinate should be initialized to 0.0."


def test_translate_position(agent: Agent) -> None:
    """
    Test that the agent's position is correctly updated after translation of the 2D shapes.

    Parameters
    ----------
    agent : Agent
        The agent fixture.
    """
    initial_position = agent.get_position()
    agent.translate(30.0, 10.0)
    final_position = agent.get_position()
    assert abs(final_position.x - (initial_position.x + 30.0)) < 0.05, "The x-coordinate should have changed by 30.0."
    assert abs(final_position.y - (initial_position.y + 10.0)) < 0.05, "The y-coordinate should have changed by 10.0."

    initial_position = agent.get_position()
    agent.translate(-30.0, -10.0)
    final_position = agent.get_position()
    assert abs(final_position.x - (initial_position.x - 30.0)) < 0.05, "The x-coordinate should have changed by -30.0."
    assert abs(final_position.y - (initial_position.y - 10.0)) < 0.05, "The y-coordinate should have changed by -10.0."


def test_translate_body3d_xy(agent: Agent) -> None:
    """
    Test that the agent's 3D body centroid is correctly updated after translation in x and y.

    Parameters
    ----------
    agent : Agent
        The agent fixture.
    """
    initial_centroid = agent.get_centroid_body3D()
    agent.translate_body3D(30.0, 10.0, 0.0)
    final_centroid = agent.get_centroid_body3D()
    assert abs(final_centroid.x - (initial_centroid.x + 30.0)) < 0.05, "The x-coordinate should have changed by 30.0."
    assert abs(final_centroid.y - (initial_centroid.y + 10.0)) < 0.05, "The y-coordinate should have changed by 10.0."

    initial_centroid = agent.get_centroid_body3D()
    agent.translate_body3D(-30.0, -10.0, 0.0)
    final_centroid = agent.get_centroid_body3D()
    assert abs(final_centroid.x - (initial_centroid.x - 30.0)) < 0.05, "The x-coordinate should have changed by -30.0."
    assert abs(final_centroid.y - (initial_centroid.y - 10.0)) < 0.05, "The y-coordinate should have changed by -10.0."


def test_translate_body3d_z(agent: Agent) -> None:
    """
    Test that the agent's 3D body centroid and lowest altitude are correctly updated after translation in z.

    Parameters
    ----------
    agent : Agent
        The agent fixture.
    """
    initial_centroid = agent.get_centroid_body3D()
    initial_lowest_altitude = min(agent.shapes3D.shapes.keys())
    agent.translate_body3D(0.0, 0.0, 30.0)
    final_centroid = agent.get_centroid_body3D()
    final_lowest_altitude = min(agent.shapes3D.shapes.keys())
    assert abs(final_centroid.x - initial_centroid.x) < 0.05, "The x-coordinate should not have changed."
    assert abs(final_centroid.y - initial_centroid.y) < 0.05, "The y-coordinate should not have changed."
    assert abs(final_lowest_altitude - (initial_lowest_altitude + 30.0)) < 0.05, "The lowest altitude should have changed by 30.0."

    initial_centroid = agent.get_centroid_body3D()
    initial_lowest_altitude = min(agent.shapes3D.shapes.keys())
    agent.translate_body3D(0.0, 0.0, -30.0)
    final_centroid = agent.get_centroid_body3D()
    final_lowest_altitude = min(agent.shapes3D.shapes.keys())
    assert abs(final_centroid.x - initial_centroid.x) < 0.05, "The x-coordinate should not have changed."
    assert abs(final_centroid.y - initial_centroid.y) < 0.05, "The y-coordinate should not have changed."
    assert abs(final_lowest_altitude - (initial_lowest_altitude - 30.0)) < 0.05, "The lowest altitude should have changed by -30.0."
