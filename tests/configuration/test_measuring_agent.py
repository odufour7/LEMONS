"""
Unit tests for the measuring methods of Agent 2D and 3D shapes.

Tests cover:
    - Correctness of 2D measurements (chest depth, bideltoid breadth) under rotation and translation
    - Correctness of 3D measurements (height, chest depth, bideltoid breadth) under rotation and translation
    - Validation of the smallest 3D height value after transformations
    - Consistency of measurements after multiple geometric operations
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

MEASURES: dict[str, Sex | float] = {
    "sex": "male",
    "bideltoid_breadth": 45.0,  # cm
    "chest_depth": 25.0,  # cm
    "height": 180.0,  # cm
    "weight": 75.0,  # kg
}


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
    agent_measures = AgentMeasures(agent_type=agent_type, measures=MEASURES)
    return Agent(agent_type=agent_type, measures=agent_measures)


def test_shapes2d_chest_depth(agent: Agent) -> None:
    """
    Test that the 2D chest depth is correct.

    Parameters
    ----------
    agent : Agent
        The agent fixture.
    """
    chest_depth_m = agent.shapes2D.get_chest_depth()
    expected_m = MEASURES["chest_depth"]
    assert np.isclose(chest_depth_m, expected_m, atol=0.05), f"The chest depth should be {expected_m} m."
    # rotate and check again
    agent.rotate(90.0)
    chest_depth_m = agent.shapes2D.get_chest_depth()
    assert np.isclose(chest_depth_m, expected_m, atol=0.05), f"The chest depth should be {expected_m} m."
    # translate and check again
    agent.translate(10.0, 10.0)
    chest_depth_m = agent.shapes2D.get_chest_depth()
    assert np.isclose(chest_depth_m, expected_m, atol=0.05), f"The chest depth should be {expected_m} m."
    # translate and check again
    agent.translate(-20.0, -10.0)
    chest_depth_m = agent.shapes2D.get_chest_depth()
    assert np.isclose(chest_depth_m, expected_m, atol=0.05), f"The chest depth should be {expected_m} m."
    # rotate and check again
    agent.rotate(-400.0)
    chest_depth_m = agent.shapes2D.get_chest_depth()
    assert np.isclose(chest_depth_m, expected_m, atol=0.05), f"The chest depth should be {expected_m} m."


def test_shapes2d_bideltoid_breadth(agent: Agent) -> None:
    """
    Test that the 2D bideltoid breadth is correct.

    Parameters
    ----------
    agent : Agent
        The agent fixture.
    """
    bideltoid_breadth_m = agent.shapes2D.get_bideltoid_breadth()
    expected_m = MEASURES["bideltoid_breadth"]
    assert np.isclose(bideltoid_breadth_m, expected_m, atol=0.1), f"The bideltoid breadth should be {expected_m} m."
    # rotate and check again
    agent.rotate(90.0)
    bideltoid_breadth_m = agent.shapes2D.get_bideltoid_breadth()
    assert np.isclose(bideltoid_breadth_m, expected_m, atol=0.1), f"The bideltoid breadth should be {expected_m} m."
    # translate and check again
    agent.translate(10.0, 10.0)
    bideltoid_breadth_m = agent.shapes2D.get_bideltoid_breadth()
    assert np.isclose(bideltoid_breadth_m, expected_m, atol=0.1), f"The bideltoid breadth should be {expected_m} m."
    # translate and check again
    agent.translate(-20.0, -10.0)
    bideltoid_breadth_m = agent.shapes2D.get_bideltoid_breadth()
    assert np.isclose(bideltoid_breadth_m, expected_m, atol=0.1), f"The bideltoid breadth should be {expected_m} m."
    # rotate and check again
    agent.rotate(-400.0)
    bideltoid_breadth_m = agent.shapes2D.get_bideltoid_breadth()
    assert np.isclose(bideltoid_breadth_m, expected_m, atol=0.1), f"The bideltoid breadth should be {expected_m} m."


def test_shapes3d_height(agent: Agent) -> None:
    """
    Test that the 3D height is correct (in centimeters).

    Parameters
    ----------
    agent : Agent
        The agent fixture.
    """
    height_cm = agent.shapes3D.get_height()
    expected_cm = MEASURES["height"]
    assert np.isclose(height_cm, expected_cm, atol=0.05), f"The height should be {expected_cm} cm."
    # rotate and check again
    agent.rotate_body3D(90.0)
    height_cm = agent.shapes3D.get_height()
    assert np.isclose(height_cm, expected_cm, atol=0.05), f"The height should be {expected_cm} cm."
    # translate and check again
    agent.translate_body3D(10.0, 10.0, 0.0)
    height_cm = agent.shapes3D.get_height()
    assert np.isclose(height_cm, expected_cm, atol=0.05), f"The height should be {expected_cm} cm."
    # rotate and check again
    agent.rotate_body3D(90.0)
    height_cm = agent.shapes3D.get_height()
    assert np.isclose(height_cm, expected_cm, atol=0.05), f"The height should be {expected_cm} cm."
    # translate and check again
    agent.translate_body3D(0.0, 0.0, -50.0)
    height_cm = agent.shapes3D.get_height()
    assert np.isclose(height_cm, expected_cm, atol=0.05), f"The height should be {expected_cm} cm."


def test_shapes3d_smallest_height(agent: Agent) -> None:
    """
    Test that the smallest height in the 3D shapes is 0.0.

    Parameters
    ----------
    agent : Agent
        The agent fixture.
    """
    smallest_height = min(agent.shapes3D.shapes.keys())
    assert np.isclose(float(smallest_height), 0.0, atol=0.1), "The smallest height should be 0.0 cm."
    # rotate and check again
    agent.rotate_body3D(90.0)
    smallest_height = min(agent.shapes3D.shapes.keys())
    assert np.isclose(float(smallest_height), 0.0, atol=0.1), "The smallest height should be 0.0 cm."
    # translate and check again
    agent.translate_body3D(10.0, 10.0, 0.0)
    smallest_height = min(agent.shapes3D.shapes.keys())
    assert np.isclose(float(smallest_height), 0.0, atol=0.1), "The smallest height should be 0.0 cm."
    # translate and check again
    agent.translate_body3D(0.0, 0.0, -50.0)
    smallest_height = min(agent.shapes3D.shapes.keys())
    assert np.isclose(float(smallest_height), -50.0, atol=0.1), "The smallest height should be -50.0 cm."


def test_shapes3d_bideltoid_and_chest_depth(agent: Agent) -> None:
    """
    Test that the 3D bideltoid breadth and chest depth are correct (in centimeters).

    Parameters
    ----------
    agent : Agent
        The agent fixture.
    """
    agent.rotate_body3D(90.0)  # rotate to 90 degrees to be able to compute the bideltoid breadth and chest depth
    bideltoid_breadth = agent.shapes3D.get_bideltoid_breadth()
    chest_depth = agent.shapes3D.get_chest_depth()
    assert np.isclose(bideltoid_breadth, MEASURES["bideltoid_breadth"], atol=0.5), (
        f"The bideltoid breadth should be {MEASURES['bideltoid_breadth']} cm."
    )
    assert np.isclose(chest_depth, MEASURES["chest_depth"], atol=0.5), f"The chest depth should be {MEASURES['chest_depth']} cm."
    # translate and check again
    agent.translate_body3D(10.0, 10.0, 10.0)
    bideltoid_breadth = agent.shapes3D.get_bideltoid_breadth()
    chest_depth = agent.shapes3D.get_chest_depth()
    assert np.isclose(bideltoid_breadth, MEASURES["bideltoid_breadth"], atol=0.5), (
        f"The bideltoid breadth should be {MEASURES['bideltoid_breadth']} cm."
    )
    assert np.isclose(chest_depth, MEASURES["chest_depth"], atol=0.5), f"The chest depth should be {MEASURES['chest_depth']} cm."
    # translate and check again
    agent.translate_body3D(-20.0, -10.0, -50.0)
    bideltoid_breadth = agent.shapes3D.get_bideltoid_breadth()
    chest_depth = agent.shapes3D.get_chest_depth()
    assert np.isclose(bideltoid_breadth, MEASURES["bideltoid_breadth"], atol=0.5), (
        f"The bideltoid breadth should be {MEASURES['bideltoid_breadth']} cm."
    )
    assert np.isclose(chest_depth, MEASURES["chest_depth"], atol=0.5), f"The chest depth should be {MEASURES['chest_depth']} cm."
