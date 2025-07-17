"""Module containing the Crowd class, which represents a crowd of pedestrians in a room."""

# Copyright  2025  Institute of Light and Matter, CNRS UMR 5306, University Claude Bernard Lyon 1
# Contributors: Oscar DUFOUR, Maxime STAPELLE, Alexandre NICOLAS

# This software is a computer program designed to generate a realistic crowd from anthropometric data and
# simulate the mechanical interactions that occur within it and with obstacles.

# This software is governed by the CeCILL  license under French law and abiding by the rules of distribution
# of free software.  You can  use, modify and/ or redistribute the software under the terms of the CeCILL
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

# The fact that you are presently reading this means that you have had knowledge of the CeCILL license and that
# you accept its terms.

import numpy as np
import shapely.affinity as affin
from numpy.typing import NDArray
from shapely.geometry import Point, Polygon

import configuration.utils.constants as cst
from configuration.models.agents import Agent
from configuration.models.measures import CrowdMeasures, create_pedestrian_measures, draw_agent_measures, draw_agent_type
from configuration.models.shapes2D import Shapes2D
from configuration.utils.typing_custom import DynamicCrowdDataType, GeometryDataType, StaticCrowdDataType


class Crowd:
    """
    Class representing a crowd of pedestrians in a room.

    Parameters
    ----------
    measures : dict[str, float] | CrowdMeasures | None
        Crowd measures data. Can be:
            - A dictionary of agent statistics (str keys, float values)
            - A CrowdMeasures instance
            - None (default) when agents are provided instead
    agents : list[Agent] | None
        List of Agent instances. If None, measures must be provided.
        When agents are provided, crowd statistics will be calculated from them.
    boundaries : Polygon | None
        A shapely Polygon instance defining the boundaries.
        If None, a default large square boundary is created.
    """

    def __init__(
        self,
        measures: dict[str, float] | CrowdMeasures | None = None,
        agents: list[Agent] | None = None,
        boundaries: Polygon | None = None,
    ) -> None:
        """
        Initialize the class instance with measures, agents, and boundaries.

        Parameters
        ----------
        measures : dict[str, float] | CrowdMeasures | None
            Crowd measures data. Can be:
                - A dictionary of agent statistics (str keys, float values)
                - A CrowdMeasures instance
                - None (default) when agents are provided instead
        agents : list[Agent] | None
            List of Agent instances. If None, measures must be provided or default will be used.
            When agents are provided, crowd statistics will be calculated from them.
        boundaries : Polygon | None
            A shapely Polygon instance defining the boundaries.
            If None, a default large square boundary is created.

        Raises
        ------
        ValueError
            If both measures and agents are provided, or if the provided arguments are of incorrect types.
        """
        # Only allow one of: (measures is not None and agents is None), (measures is None and agents is not None),
        # or (measures is None and agents is None)
        if measures is not None and agents is not None:
            raise ValueError("You must provide only one of 'measures' or 'agents', or neither (not both).")

        # Boundaries validation
        if boundaries is None:
            boundaries = Polygon()
        elif not isinstance(boundaries, Polygon):
            raise ValueError("'boundaries' should be a shapely Polygon instance even if empty")

        # If agents are provided (measures must be None)
        if agents is not None:
            if not isinstance(agents, list):
                raise ValueError("'agents' should be a list of Agent instances")
            if agents and not all(isinstance(agent, Agent) for agent in agents):
                raise ValueError("All elements in 'agents' must be Agent instances")
            self._agents = agents
            # Calculate measures from agents
            self._measures = CrowdMeasures(agent_statistics=self.get_crowd_statistics()["measures"])
        # If measures are provided (agents must be None)
        elif measures is not None:
            if isinstance(measures, CrowdMeasures):
                self._measures = measures
            elif isinstance(measures, dict):
                if not measures:
                    self._measures = CrowdMeasures()
                elif all(isinstance(k, str) and isinstance(v, (int, float)) for k, v in measures.items()):
                    self._measures = CrowdMeasures(agent_statistics=measures)
                else:
                    raise ValueError("If 'measures' is a dictionary, it must have string keys and numeric values")
            else:
                raise ValueError("'measures' should be None, a dict[str, float] or a CrowdMeasures instance")
            self._agents = []
        # If both are None, use defaults
        else:
            self._measures = CrowdMeasures()
            self._agents = []

        self._boundaries = boundaries

    @property
    def agents(self) -> list[Agent]:
        """
        Get the list of agents in the crowd.

        Returns
        -------
        list[Agent]
            A list containing all the agents in the crowd.
        """
        return self._agents

    @agents.setter
    def agents(self, value: list[Agent]) -> None:
        """
        Set the agents of the crowd.

        Parameters
        ----------
        value : list[Agent]
            A list of Agent instances.

        Raises
        ------
        ValueError
            If `value` is not a list or if any element in `value` is not an instance of Agent.
        """
        if not isinstance(value, list) or not all(isinstance(agent, Agent) for agent in value):
            raise ValueError("'agents' should be a list of Agent instances")
        self._agents = value
        self._measures.agent_statistics = self.get_crowd_statistics()["measures"]

    @property
    def measures(self) -> CrowdMeasures:
        """
        Get the measures of the crowd.

        Returns
        -------
        CrowdMeasures
            A CrowdMeasures object containing the measures of the crowd.
        """
        return self._measures

    @property
    def boundaries(self) -> Polygon:
        """
        Get the boundaries of the room.

        Returns
        -------
        Polygon
            The boundaries of the room as a shapely Polygon object.
        """
        return self._boundaries

    @boundaries.setter
    def boundaries(self, value: Polygon) -> None:
        """
        Set the boundaries of the room.

        Parameters
        ----------
        value : Polygon
            A shapely Polygon instance representing the boundaries of the room.

        Raises
        ------
        ValueError
            If `value` is not an instance of shapely Polygon.
        """
        if not isinstance(value, Polygon):
            raise ValueError("'boundaries' should be a shapely Polygon instance")
        self._boundaries = value

    def get_number_agents(self) -> int:
        """
        Get the number of agents in the crowd.

        Returns
        -------
        int
            The number of agents in the crowd.
        """
        return len(self._agents)

    def add_one_agent(self) -> None:
        """
        Add a new agent to the crowd using available measures data.

        The agent creation follows this priority:
        1. Uses agent statistics if available
        2. Uses the default ANSURII database
        """
        # Case 1: Use agent statistics if available and custom database is empty
        if self.measures.agent_statistics:
            drawn_agent_type = draw_agent_type(self.measures)
            drawn_agent_measures = draw_agent_measures(drawn_agent_type, self.measures)
            self.agents.append(Agent(agent_type=drawn_agent_type, measures=drawn_agent_measures))

        # Case 2: Use the default ANSURII database if no other data is available
        elif not self.measures.agent_statistics:
            drawn_agent_data = np.random.choice(np.array(list(self.measures.default_database.values()), dtype="object"))
            agent_measures = create_pedestrian_measures(drawn_agent_data)
            self.agents.append(Agent(agent_type=cst.AgentTypes.pedestrian, measures=agent_measures))

    def create_agents(self, number_agents: int = cst.DEFAULT_AGENT_NUMBER) -> None:
        """
        Create multiple agents in the crowd from the given CrowdMeasures (ANSURII database by default).

        Parameters
        ----------
        number_agents : int
            Number of agents to create.
        """
        for _ in range(number_agents):
            self.add_one_agent()

    def calculate_interpenetration(self) -> tuple[float, float]:
        """
        Compute the total interpenetration area between pedestrians and between pedestrians and boundaries.

        Returns
        -------
        float
            The total interpenetration area between pedestrians and between pedestrians and boundaries.
        """
        interpenetration_between_agents = 0.0
        interpenetration_with_boundaries = 0.0
        n_agents = self.get_number_agents()

        # Loop over all agents in the crowd
        for i_agent, current_agent in enumerate(self.agents):
            current_geometric = current_agent.shapes2D.get_geometric_shape()
            # Loop over all other agents in the crowd
            for j in range(i_agent + 1, n_agents):
                neigh_agent = self.agents[j]
                neigh_geometric = neigh_agent.shapes2D.get_geometric_shape()
                # Compute interpenetration between current agent and neighbor
                interpenetration_between_agents += current_geometric.intersection(neigh_geometric).area
            # Compute interpenetration with the boundaries
            interpenetration_with_boundaries += current_geometric.difference(self.boundaries).area

        return interpenetration_between_agents, interpenetration_with_boundaries

    @staticmethod
    def calculate_contact_force(agent_centroid: Point, other_centroid: Point) -> NDArray[np.float64]:
        """
        Compute the repulsive force between two centroids.

        Parameters
        ----------
        agent_centroid : Point
            The centroid of the agent.
        other_centroid : Point
            The centroid of the other agent.

        Returns
        -------
        NDArray[np.float64]
            The normalized direction of the repulsive force as a 1D NumPy array of floats.
            If the centroids coincide, a small random force is returned.
        """
        # Extract coordinates from Shapely Points and convert them to NumPy arrays
        agent_coords = np.array(agent_centroid.coords[0], dtype=np.float64)
        other_coords = np.array(other_centroid.coords[0], dtype=np.float64)

        # Compute the difference vector between centroids
        delta = agent_coords - other_coords

        # Compute the norm (magnitude) of the difference vector
        norm_delta = np.linalg.norm(delta)

        # If the norm is greater than zero, normalize the difference vector
        if norm_delta > 0:
            return np.array(cst.INTENSITY_TRANSLATIONAL_FORCE * delta / norm_delta)  # Return normalized direction of the force

        # If centroids coincide, return a small random force as a fallback
        return np.random.rand(2).astype(np.float64)

    @staticmethod
    def calculate_repulsive_force(
        agent_centroid: Point,
        other_centroid: Point,
        repulsion_length: float,
    ) -> NDArray[np.float64]:
        """
        Compute the repulsive force between two centroids, exponentially decreasing with distance.

        Parameters
        ----------
        agent_centroid : Point
            The centroid of the agent.
        other_centroid : Point
            The centroid of the other agent.
        repulsion_length : float
            Coefficient used to compute the magnitude of the repulsive force between agents.
            The force decreases exponentially with distance divided by this repulsion_length.

        Returns
        -------
        NDArray[np.float64]
            A 1D NumPy array representing the repulsive force vector.
            If the centroids coincide, a small random force is returned.
        """
        # Extract coordinates from Shapely Points and convert them to NumPy arrays
        agent_coords = np.array(agent_centroid.coords[0], dtype=np.float64)
        other_coords = np.array(other_centroid.coords[0], dtype=np.float64)

        # Compute the difference vector between centroids
        delta = agent_coords - other_coords

        # Compute the norm (magnitude) of the difference vector
        norm_delta = np.linalg.norm(delta)

        # Handle edge case where centroids coincide (norm_delta == 0)
        if norm_delta == 0:
            return np.random.rand(2).astype(np.float64)  # Small random force as fallback

        # Normalize the difference vector to get the direction of the force
        direction = delta / norm_delta

        # Compute the magnitude of the repulsive force (exponentially decreasing with distance)
        force_magnitude = np.exp(-norm_delta / repulsion_length)

        # Return the repulsive force vector as a NumPy array
        return np.array(force_magnitude * direction)

    @staticmethod
    def calculate_rotational_force(temperature: float) -> float:
        """
        Generate a random rotational force value.

        Parameters
        ----------
        temperature : float
            Current cooling system coefficient (0.0-1.0) that scales rotational forces.

        Returns
        -------
        float
            Random rotational force in degrees.
        """
        return float(np.random.uniform(-cst.INTENSITY_ROTATIONAL_FORCE, cst.INTENSITY_ROTATIONAL_FORCE, 1)[0]) * temperature

    def calculate_boundary_forces(self, current_geo: Polygon, temperature: float) -> NDArray[np.float64]:
        """
        Compute boundary interaction forces for an agent near environment edges.

        Parameters
        ----------
        current_geo : Polygon
            Shapely Polygon representing the agent's current geometric position.
        temperature : float
            Current cooling system coefficient [0.0-1.0] that scales rotational forces.

        Returns
        -------
        NDArray[np.float64]
            Updated force vector with boundary interactions.

        Notes
        -----
        - Forces are only applied when the agent is outside the boundaries or touching boundary edges.
        - Force calculations:
            1. Contact force: Linear repulsion from nearest boundary point.
            2. Rotational force: Temperature-scaled random torque.
        """
        # Compute the nearest point on the agent between the agent and the boundary
        nearest_point = Point(
            self.boundaries.exterior.interpolate(
                self.boundaries.exterior.project(current_geo.centroid),
            ).coords[0]  # Compute projection distance along boundary
        )
        wall_contact_force = Crowd.calculate_contact_force(current_geo.centroid, nearest_point)
        wall_rotational_force = Crowd.calculate_rotational_force(temperature)
        wall_forces: NDArray[np.float64] = np.concatenate((wall_contact_force, np.array([wall_rotational_force])))

        return wall_forces

    @staticmethod
    def check_validity_parameters_agents_packing(
        repulsion_length: float, desired_direction: float, variable_orientation: bool
    ) -> None:
        """
        Validate the input parameters for agent packing.

        Parameters
        ----------
        repulsion_length : float
            The repulsion length.
        desired_direction : float
            The desired direction.
        variable_orientation : bool
            A flag indicating whether variable orientation is enabled.
        """
        if not isinstance(repulsion_length, float):
            raise TypeError("`repulsion_length` should be a float.")
        if not isinstance(desired_direction, float):
            raise TypeError("`desired_direction` should be a float.")
        if not isinstance(variable_orientation, bool):
            raise TypeError("`variable_orientation` should be a boolean.")
        if repulsion_length <= 0:
            raise ValueError("`repulsion_length` should be a strictly positive float.")

    def update_shapes3D_based_on_shapes2D(self) -> None:
        """
        Update the position and orientation of 3D shapes of all agents based on their 2D shapes.

        This method iterates through each agent in the crowd and updates its 3D shapes position and orientation
        based on the corresponding 2D shapes.
        """
        for agent in self.agents:
            desired_orientation = agent.get_agent_orientation()
            actual_orientation = 0.0
            agent.rotate_body3D(desired_orientation - actual_orientation)
            desired_position = agent.get_position()
            actual_position = agent.get_centroid_body3D()
            actual_lowest_height = min(float(height) for height in agent.shapes3D.shapes.keys())
            agent.translate_body3D(
                dx=desired_position.x - actual_position.x,
                dy=desired_position.y - actual_position.y,
                dz=0.0 - actual_lowest_height,
            )

    def translate_crowd(self, dx: float, dy: float) -> None:
        """
        Translate all agents in the crowd by a specified offset.

        Parameters
        ----------
        dx : float
            The offset to translate in the x-direction.
        dy : float
            The offset to translate in the y-direction.
        """
        for agent in self.agents:
            agent.translate(dx, dy)
        self.boundaries = affin.translate(self.boundaries, dx, dy)

        # Update the 3d shapes only if all agents are pedestrians
        if all(agent.agent_type == cst.AgentTypes.pedestrian for agent in self.agents):
            self.update_shapes3D_based_on_shapes2D()

    def pack_agents_with_forces(
        self,
        repulsion_length: float = cst.DEFAULT_REPULSION_LENGTH,
        desired_direction: float = cst.DEFAULT_DESIRED_DIRECTION,
        variable_orientation: bool = cst.DEFAULT_VARIABLE_ORIENTATION,
    ) -> None:
        """
        Simulate crowd dynamics using physics-based forces to resolve agent overlaps.

        Iteratively calculates repulsive forces between agents and boundary constraints,
        while applying rotational adjustments. Implements a temperature-based cooling
        system to gradually reduce movement intensity over iterations.

        Parameters
        ----------
        repulsion_length : float
            Exponential decay coefficient for repulsive forces between agents.
            Higher values increase the effective range of repulsion.
        desired_direction : float
            Initial orientation angle in degrees for all agents.
        variable_orientation : bool
            Whether to apply rotational forces during packing. When True, enables
            random angular adjustments based on collision forces.

        Notes
        -----
        - Boundary handling:
            * Uses Shapely Polygon objects for boundary constraints
            * Agents cannot move outside boundary polygons
            * Boundaries are treated as static
        - Force calculations:
            1. Agent-agent repulsion (exponential decay with distance)
            2. Contact forces for overlapping agents
            3. Boundary repulsion for agents near edges
            4. Rotational forces (only when variable_orientation=True)
        """
        Crowd.check_validity_parameters_agents_packing(
            repulsion_length=repulsion_length,
            desired_direction=desired_direction,
            variable_orientation=variable_orientation,
        )

        # Initially, all agents have 0° orientation (head facing right) and are at (0,0),
        # so we need to rotate them to the desired direction and translate them to the center of the boundaries
        for current_agent in self.agents:
            center_of_boundaries = self.boundaries.centroid if not self.boundaries.is_empty else Point(0.0, 0.0)
            current_agent.translate(center_of_boundaries.x, center_of_boundaries.y)
            current_agent.rotate(desired_direction)

        Temperature = cst.INITIAL_TEMPERATURE
        for _ in range(cst.MAX_NB_ITERATIONS):
            # Check for overlaps and apply forces if necessary
            for i_agent, current_agent in enumerate(self.agents):
                # Format: [x_translation (cm), y_translation (cm), rotation (degrees)]
                forces: NDArray[np.float64] = np.array([0.0, 0.0, 0.0])
                current_geometric = current_agent.shapes2D.get_geometric_shape()
                current_centroid: Point = current_geometric.centroid

                # Compute repulsive force between agents
                for j_agent, neigh_agent in enumerate(self.agents):
                    if i_agent == j_agent:
                        continue
                    neigh_geometric = neigh_agent.shapes2D.get_geometric_shape()
                    neigh_centroid: Point = neigh_geometric.centroid
                    forces[:-1] += Crowd.calculate_repulsive_force(current_centroid, neigh_centroid, repulsion_length)
                    if current_geometric.intersects(neigh_geometric):
                        forces[:-1] += Crowd.calculate_contact_force(current_centroid, neigh_centroid)
                        forces[-1] += Crowd.calculate_rotational_force(Temperature)

                # Compute repulsive force between agent and wall
                if not (self.boundaries.is_empty or self.boundaries.contains(current_geometric)):
                    forces += self.calculate_boundary_forces(current_geometric, Temperature)

                # Rotate pedestrian
                if variable_orientation:
                    current_agent.rotate(forces[-1])

                # Translate pedestrian
                new_position = Point(np.array(current_centroid.coords[0], dtype=np.float64) + forces[:-1])
                if self.boundaries.is_empty:
                    current_agent.translate(forces[:-1][0], forces[:-1][1])
                elif self.boundaries.contains(new_position):
                    current_agent.translate(forces[:-1][0], forces[:-1][1])

            # Decrease the temperature at each iteration
            Temperature = max(0.0, Temperature - cst.ADDITIVE_COOLING)

        # If no boundaries translate all agents and wall to get the minimum x-coordinates and minimum y-coordinates at (0., 0.)
        if self.boundaries.is_empty:
            min_x = min(min(agent.shapes2D.get_geometric_shape().bounds[0] for agent in self.agents), self.boundaries.bounds[0])
            min_y = min(min(agent.shapes2D.get_geometric_shape().bounds[1] for agent in self.agents), self.boundaries.bounds[1])
        else:
            min_x = min(x for x, _ in self.boundaries.exterior.coords)
            min_y = min(y for _, y in self.boundaries.exterior.coords)
        self.translate_crowd(-min_x, -min_y)

    def unpack_crowd(self) -> None:
        """Translate all agents in the crowd to the origin (0, 0)."""
        for agent in self.agents:
            current_position: Point = agent.get_position()
            translation_vector = np.array([-current_position.x, -current_position.y])
            agent.translate(*translation_vector)

    def pack_agents_on_grid(self, grid_size_x: float = cst.GRID_SIZE_X, grid_size_y: float = cst.GRID_SIZE_Y) -> None:
        """
        Arrange the agents on a square 2D grid with specified cell sizes, ensuring that the smallest x and y coordinates are at (0, 0).

        Parameters
        ----------
        grid_size_x : float
            Width of each grid cell (distance between agents in x-direction).
        grid_size_y : float
            Height of each grid cell (distance between agents in y-direction).
        """
        best_n_cols, min_diff = 1, float("inf")

        for n_cols in range(1, self.get_number_agents() + 1):
            n_rows = (self.get_number_agents() + n_cols - 1) // n_cols
            diff = abs(n_cols * grid_size_x - n_rows * grid_size_y)
            if diff < min_diff:
                min_diff, best_n_cols = diff, n_cols

        x_offset = -min(agent.shapes2D.get_geometric_shape().bounds[0] for agent in self.agents)
        y_offset = -min(agent.shapes2D.get_geometric_shape().bounds[1] for agent in self.agents)

        for i, agent in enumerate(self.agents):
            pos = agent.get_position()
            col, row = i % best_n_cols, i // best_n_cols
            agent.translate(col * grid_size_x + x_offset - pos.x, row * grid_size_y + y_offset - pos.y)

        if all(agent.agent_type == cst.AgentTypes.pedestrian for agent in self.agents):
            self.update_shapes3D_based_on_shapes2D()

    @staticmethod
    def compute_stats(data: list[float | None], stats_key: str) -> float | None:
        """
        Compute statistics.

        Parameters
        ----------
        data : list[float | None]
            The list of numerical values to compute statistics for.
        stats_key : str
            The type of statistic to compute ('mean', 'std_dev', 'min', 'max').

        Returns
        -------
        float | None
            The computed statistic or None if data is empty or invalid.
        """
        # Filter out None values
        filtered = [x for x in data if x is not None]

        if not filtered:
            return None

        if "mean" in stats_key:
            return float(np.mean(filtered, dtype=float))
        if "std_dev" in stats_key:
            return float(np.std(filtered, ddof=1, dtype=float)) if len(filtered) >= 2 else None
        if "min" in stats_key:
            return float(np.min(filtered))
        if "max" in stats_key:
            return float(np.max(filtered))
        raise ValueError(f"Unknown stats key: {stats_key}")

    def get_crowd_statistics(self) -> dict[str, dict[str, int] | dict[str, list[float | None]] | dict[str, float | int | None]]:
        """
        Measure the statistics of the crowd.

        Returns
        -------
        dict[str, dict[str, int] | dict[str, list[float | None]] | dict[str, float | int | None]]
            A dictionary whose keys and values are:
                - stats_counts: A dictionary with counts of agents by type.
                - stats_lists: A dictionary with lists of measurements for each agent type.
                - measures: A dictionary of computed statistics for the crowd.

        Notes
        -----
        The dictionary containing the computed statistics for the crowd has keys formatted as follows:
            - "{kind}_proportion": Count of agents (e.g., "male_proportion" or "bike_proportion" or "pedestrian_proportion")
            - "{part}_mean": Mean value for each body/bike part measurement
            - "{part}_std_dev": Sample standard deviation for each part
            - "{part}_min": Minimum observed value for each part
            - "{part}_max": Maximum observed value for each part
        The dictionary containing the counts of agents by type has keys formatted as follows:
            - "pedestrian_number": Total number of pedestrians
            - "male_number": Total number of males
            - "bike_number": Total number of bikes
        The dictionary containing the lists of measurements for each agent type has keys formatted as follows:
            - "bike_weight": List of weights for all bikes
            - "male_bideltoid_breadth": List of bideltoid breadths for all male pedestrians
            - "male_chest_depth": List of chest depths for all male pedestrians
            - "male_height": List of heights for all male pedestrians
            - "male_weight": List of weights for all male pedestrians
            - "female_bideltoid_breadth": List of bideltoid breadths for all female pedestrians
            - "female_chest_depth": List of chest depths for all female pedestrians
            - "female_height": List of heights for all female pedestrians
            - "female_weight": List of weights for all female pedestrians
            - "wheel_width": List of wheel widths for all bikes
            - "total_length": List of total lengths for all bikes
            - "handlebar_length": List of handlebar lengths for all bikes
            - "top_tube_length": List of top tube lengths for all bikes
        """
        # Initialize statistics dictionary
        stats_counts: dict[str, int] = {
            "pedestrian_number": 0,
            "male_number": 0,
            "bike_number": 0,
        }
        stats_lists: dict[str, list[float | None]] = {
            "male_bideltoid_breadth": [],
            "male_chest_depth": [],
            "male_height": [],
            "male_weight": [],
            "female_bideltoid_breadth": [],
            "female_chest_depth": [],
            "female_height": [],
            "female_weight": [],
            "wheel_width": [],
            "total_length": [],
            "handlebar_length": [],
            "top_tube_length": [],
            "bike_weight": [],
        }

        # Collect data from agents
        for agent in self.agents:
            weight = agent.measures.measures[cst.CommonMeasures.weight.name]
            if agent.agent_type == cst.AgentTypes.pedestrian:
                stats_counts["pedestrian_number"] += 1
                bideltoid_breadth = agent.measures.measures[cst.PedestrianParts.bideltoid_breadth.name]
                chest_depth = agent.measures.measures[cst.PedestrianParts.chest_depth.name]
                height = agent.measures.measures[cst.PedestrianParts.height.name]
                if agent.measures.measures["sex"] == "male":
                    stats_counts["male_number"] += 1
                    stats_lists["male_bideltoid_breadth"].append(bideltoid_breadth)
                    stats_lists["male_chest_depth"].append(chest_depth)
                    stats_lists["male_height"].append(height)
                    stats_lists["male_weight"].append(weight)
                else:
                    stats_lists["female_bideltoid_breadth"].append(bideltoid_breadth)
                    stats_lists["female_chest_depth"].append(chest_depth)
                    stats_lists["female_height"].append(height)
                    stats_lists["female_weight"].append(weight)

            elif agent.agent_type == cst.AgentTypes.bike:
                stats_counts["bike_number"] += 1
                stats_lists["bike_weight"].append(weight)
                stats_lists["wheel_width"].append(agent.measures.measures[cst.BikeParts.wheel_width.name])
                stats_lists["total_length"].append(agent.measures.measures[cst.BikeParts.total_length.name])
                stats_lists["handlebar_length"].append(agent.measures.measures[cst.BikeParts.handlebar_length.name])
                stats_lists["top_tube_length"].append(agent.measures.measures[cst.BikeParts.top_tube_length.name])

        # Compute proportions
        total_agents: int = self.get_number_agents()
        measures: dict[str, float | int | None] = {
            "male_proportion": stats_counts["male_number"] / stats_counts["pedestrian_number"]
            if stats_counts["pedestrian_number"] > 0
            else None,
            "pedestrian_proportion": stats_counts["pedestrian_number"] / total_agents if total_agents > 0 else None,
            "bike_proportion": stats_counts["bike_number"] / total_agents if total_agents > 0 else None,
        }

        # Compute detailed statistics for relevant keys
        for part_key in [
            "male_bideltoid_breadth",
            "male_chest_depth",
            "male_height",
            "male_weight",
            "female_bideltoid_breadth",
            "female_chest_depth",
            "female_height",
            "female_weight",
            "wheel_width",
            "total_length",
            "handlebar_length",
            "top_tube_length",
            "bike_weight",
        ]:
            for stats_key in ["_min", "_max", "_mean", "_std_dev"]:
                measures[part_key + stats_key] = Crowd.compute_stats(stats_lists[part_key], stats_key)

        return {
            "stats_counts": stats_counts,
            "stats_lists": stats_lists,
            "measures": measures,
        }


def create_agents_from_dynamic_static_geometry_parameters(
    static_dict: StaticCrowdDataType, dynamic_dict: DynamicCrowdDataType, geometry_dict: GeometryDataType
) -> Crowd:
    """
    Create agents from dynamic and static geometry parameters.

    Parameters
    ----------
    static_dict : StaticCrowdDataType
        Dictionary containing static crowd data.
    dynamic_dict : DynamicCrowdDataType
        Dictionary containing dynamic crowd data.
    geometry_dict : GeometryDataType
        Dictionary containing geometry data.

    Returns
    -------
    Crowd
        A Crowd object containing the created agents and the scene boundaries.
    """
    # --- Extract wall polygons and set boundaries ---
    wall_polygons = [
        Polygon(
            [
                [corner["Coordinates"][0] * cst.M_TO_CM, corner["Coordinates"][1] * cst.M_TO_CM]
                for corner in wall_data["Corners"].values()
            ]
        )
        for wall_data in geometry_dict.get("Geometry", {}).get("Wall", {}).values()
    ]
    if not wall_polygons:
        raise ValueError("No wall polygons found in geometry_dict.")
    boundaries: Polygon = max(wall_polygons, key=lambda polygon: polygon.area)  # Set the largest polygon as boundaries

    # --- Extract agent positions and orientations ---
    agent_positions = {agent["Id"]: agent["Kinematics"]["Position"] for agent in dynamic_dict.get("Agents", {}).values()}
    agent_orientations = {agent["Id"]: agent["Kinematics"]["Theta"] for agent in dynamic_dict.get("Agents", {}).values()}

    # --- Create agents ---
    all_agents = []
    for agent_data in static_dict.get("Agents", {}).values():
        if agent_data.get("Type") != cst.AgentTypes.pedestrian.name.lower():  # Skip non-pedestrian agents
            continue

        agent_id: int = agent_data["Id"]
        wanted_center_of_mass: tuple[float, float] = agent_positions.get(agent_id, (0.0, 0.0))  # m
        wanted_center_of_mass = np.array(wanted_center_of_mass) * cst.M_TO_CM  # cm
        wanted_orientation: float = np.degrees(agent_orientations.get(agent_id, 0.0))  # radian

        agent_shape2D = Shapes2D(agent_type=cst.AgentTypes.pedestrian)

        for shape_name, shape_data in agent_data.get("Shapes", {}).items():
            # Calculate global position of the shape
            rel_x, rel_y = shape_data["Position"]  # m
            agent_shape2D.add_shape(
                name=shape_name,
                shape_type=cst.ShapeTypes.disk.name,
                material=cst.MaterialNames.human_naked.name,
                radius=shape_data["Radius"] * cst.M_TO_CM,
                x=rel_x * cst.M_TO_CM,
                y=rel_y * cst.M_TO_CM,
            )

        agent_measures = {
            "sex": "male",
            "bideltoid_breadth": agent_shape2D.get_bideltoid_breadth(),
            "chest_depth": agent_shape2D.get_chest_depth(),
            "height": agent_data["Height"] * cst.M_TO_CM,  # m
            "weight": agent_data["Mass"],  # kg
        }
        new_agent = Agent(agent_type=cst.AgentTypes.pedestrian, measures=agent_measures)

        actual_position = new_agent.get_position()
        actual_orientation = new_agent.get_agent_orientation()
        new_agent.translate(wanted_center_of_mass[0] - actual_position.x, wanted_center_of_mass[1] - actual_position.y)
        new_agent.rotate(wanted_orientation - actual_orientation)

        current_position = new_agent.get_centroid_body3D()
        new_agent.translate_body3D(
            dx=wanted_center_of_mass[0] - current_position.x, dy=wanted_center_of_mass[1] - current_position.y, dz=0.0
        )
        new_agent.rotate_body3D(angle=wanted_orientation)

        all_agents.append(new_agent)

    return Crowd(agents=all_agents, boundaries=boundaries)
