"""
Unit tests for the Crowd class configuration and statistical validation.

Tests cover:
    - Agent population initialization count
    - Anthropometric statistic validation (means, proportions)
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
from configuration.models.crowd import Crowd
from configuration.models.measures import CrowdMeasures

NUMBER_AGENTS: int = 30
REPULSION_LENGTH: float = 5.0  # (cm)
DESIRED_DIRECTION: float = 90.0  # (degrees)
RANDOM_PACKING: bool = False

AGENT_STATISTICS: dict[str, float] = {
    **cst.CrowdStat,
    "male_proportion": 0.4,
    "male_bideltoid_breadth_mean": 70.0,  # cm
    "male_bideltoid_breadth_std_dev": 3.0,  # cm
}


@pytest.fixture
def crowd() -> Crowd:
    """
    Fixture to create a Crowd instance with predefined measures and agents.

    Returns
    -------
    Crowd
        An instance of Crowd with agents created and packed.
    """
    crowd_measures = CrowdMeasures(agent_statistics=AGENT_STATISTICS)
    crowd = Crowd(measures=crowd_measures)
    crowd.create_agents(number_agents=NUMBER_AGENTS)
    crowd.pack_agents_with_forces()
    return crowd


def test_crowd_number_of_agents(crowd: Crowd) -> None:
    """
    Test that the crowd contains the expected number of agents.

    Parameters
    ----------
    crowd : Crowd
        The crowd fixture.
    """
    assert crowd.get_number_agents() == NUMBER_AGENTS, f"Expected {NUMBER_AGENTS} agents, but got {crowd.get_number_agents()} agents."


def test_crowd_statistics_means_and_proportion(crowd: Crowd) -> None:
    """
    Test that measured crowd statistics are close to the expected values.

    Parameters
    ----------
    crowd : Crowd
        The crowd fixture.
    """
    measured_stats = crowd.get_crowd_statistics()["measures"]
    for key, value in measured_stats.items():
        if "mean" in key and ("pedestrian" in key or "male" in key or "female" in key):
            expected = AGENT_STATISTICS[key]
            assert np.isclose(value, expected, rtol=0.1), f"Expected {key} to be close to {expected}, but got {value}."
        if key == "male_proportion":
            expected = AGENT_STATISTICS[key]
            assert np.isclose(value, expected, atol=0.4), f"Expected {key} to be close to {expected}, but got {value}."
