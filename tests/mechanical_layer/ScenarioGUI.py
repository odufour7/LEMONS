"""Run the ``CrowdMechanics`` library for tests."""

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

import ctypes
import sys
import time
import xml.etree.ElementTree as ET
from math import pi
from pathlib import Path
from typing import Any, cast

import kivy
import numpy as np
import shapely.affinity as affin
from kivy.app import App
from kivy.config import Config
from kivy.core.text import Label as CoreLabel
from kivy.core.window import Window
from kivy.graphics import Color, Line, Mesh, Rectangle
from kivy.graphics.tesselator import Tesselator  # pylint: disable=no-name-in-module
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget
from shapely.geometry import MultiPolygon, Point, Polygon
from shapely.geometry.base import BaseGeometry

import configuration.utils.constants as cst
import configuration.utils.functions as fun
from configuration.models.agents import Agent
from configuration.models.measures import CrowdMeasures, create_pedestrian_measures

########## PARAMETERS ##########

# Define global parameters for the window size and system size
WS_X: int = 1000  # Windows Size X in Pixels
WS_Y: int = WS_X  # Windows Size Y in Pixels
M1: int = 40  # System Size X in cell coordinates
M2: int = M1  # System Size Y in cell coordinates
dx: float = 0.1  # x-spacing of gridpoints in meters
dy: float = dx  # y-spacing of gridpoints in meters
Lx: float = M1 * dx  # Layout width in meters
Ly: float = M2 * dy  # Layout height in meters
pixel_density: float = float(WS_X) / float(Lx)  # pixel density in pixels/meter
N_PIXELS_ONE: int = int(1 / dx)  # number of pixels that give value 1

# Define parameters for the agents
MAX_AGENTS: int = 50
rc = []
for _ in range(MAX_AGENTS):
    color = np.random.rand(3)
    # Avoid color that are too light
    while 0.2126 * color[0] + 0.7152 * color[1] + 0.0722 * color[2] > 0.7:
        color = np.random.rand(3)
    rc.append(color)

# Define parameters for forces and torque
BASE_VALUE_F: int = 100
BASE_VALUE_M: int = 10
# Position of the Torque button
torque_button_xs: int = WS_X - 55
torque_button_ys: int = WS_Y - 150
torque_button_size: int = 40

# Create folders for static and dynamic files
folderStatic = Path().absolute() / "static/"
folderDynamic = Path().absolute() / "dynamic/"
Path(folderStatic).mkdir(parents=True, exist_ok=True)
Path(folderDynamic).mkdir(parents=True, exist_ok=True)
interactionsFile = Path("dynamic/AgentInteractions.xml")
if interactionsFile.is_file():  # Delete a possible AgentInteractions.xml for a previous use
    interactionsFile.unlink()

# Crowd parameters
crowd_measures = CrowdMeasures()


########## AUXILIARY FUNCTIONS ##########


def get_closest_node(x: int, y: int) -> tuple[int, int]:
    """
    Get the closest grid node to a given point.

    Parameters
    ----------
    x : float
        The x-coordinate of the point.
    y : float
        The y-coordinate of the point.

    Returns
    -------
    Tuple[int, int]
        The coordinates of the closest grid node.
    """
    return (int(round(x / pixel_density / dx) * dx * pixel_density), int(round(y / pixel_density / dy) * dy * pixel_density))


def shapely_to_kivy_contours(geometry: BaseGeometry) -> list[list[float]]:
    """
    Convert a Shapely geometry (Polygon or MultiPolygon) to Kivy-compatible contours.

    Parameters
    ----------
    geometry : shapely.geometry.base.BaseGeometry
        A Shapely geometry object, either a Polygon or MultiPolygon.

    Returns
    -------
    list[list[float]]
        A list of contours, where each contour is a flat list of x, y coordinates
        suitable for Kivy tesselation.

    Notes
    -----
    - For a Polygon, the exterior and all interiors (holes) are converted to contours.
    - For a MultiPolygon, all constituent polygons are processed recursively.
    """
    contours: list[list[float]] = []
    if isinstance(geometry, Polygon):
        contours.append([coord for xy in geometry.exterior.coords for coord in xy])
        for interior in geometry.interiors:
            contours.append([coord for xy in interior.coords for coord in xy])
    elif isinstance(geometry, MultiPolygon):
        for poly in geometry.geoms:
            contours.extend(shapely_to_kivy_contours(poly))
    return contours


########## KIVY INTERFACE CLASSES ##########


class AgentKivy:
    """
    Class representing an agent in the simulation.

    Parameters
    ----------
    x : float
        The initial x-coordinate of the agent.
    y : float
        The initial y-coordinate of the agent.
    """

    def __init__(self, x: float, y: float) -> None:
        """
        Initialize an agent with position and default physical attributes.

        Parameters
        ----------
        x : float
            The initial x-coordinate of the agent.
        y : float
            The initial y-coordinate of the agent.

        Attributes
        ----------
        x : float
            The x-coordinate of the agent.
        y : float
            The y-coordinate of the agent.
        Fx : float
            The force applied in the x-direction (default: 0.0).
        Fy : float
            The force applied in the y-direction (default: 1.0).
        theta : float
            The orientation angle of the agent in radians (default: 0.0).
        torque : float
            The torque applied to the agent (default: 0.0).

        Raises
        ------
        TypeError
            If `x` or `y` is not a float or an int.
        """
        if not isinstance(x, (int, float)) or not isinstance(y, (int, float)):
            raise TypeError("x and y must be int or float")

        drawn_agent_data = np.random.choice(np.array(list(crowd_measures.default_database.values()), dtype="object"))
        agent_measures = create_pedestrian_measures(drawn_agent_data)
        current_agent_big = Agent(agent_type=cst.AgentTypes.pedestrian, measures=agent_measures)
        self.current_agent_big = current_agent_big
        agent_position: Point = self.current_agent_big.get_position()
        self.current_agent_big.translate(x * cst.M_TO_CM - agent_position.x, y * cst.M_TO_CM - agent_position.y)
        self.current_agent_big.translate_body3D(x * cst.M_TO_CM - agent_position.x, y * cst.M_TO_CM - agent_position.y, 0.0)
        agent_position_translated: Point = self.current_agent_big.get_position()
        self.x: float = agent_position_translated.x * cst.CM_TO_M
        self.y: float = agent_position_translated.y * cst.CM_TO_M
        self.vx: float = 0.0
        self.vy: float = 0.0
        self.theta: float = 0.0
        self.omega: float = 0.0
        self.Fx: float = 1.0
        self.Fy: float = 1.0
        self.torque: float = 0.0

        current_orientation = self.current_agent_big.get_agent_orientation()
        self.current_agent_big.rotate(np.rad2deg(self.theta) - current_orientation)
        self.current_agent_big.rotate_body3D(np.rad2deg(self.theta) - current_orientation)

    @property
    def target_force(self) -> tuple[float, float]:
        """
        Get the target force components of the agent.

        Returns
        -------
        tuple[float, float]
            A tuple containing the target force in the x-direction (Fx) and y-direction (Fy).
        """
        return self.Fx, self.Fy

    @target_force.setter
    def target_force(self, Fxy: tuple[float, float]) -> None:
        """
        Set the target force components attribute of `Agent`.

        Parameters
        ----------
        Fxy :  tuple[float, float]
            The target force in the x and y directions.
        """
        self.Fx = Fxy[0]
        self.Fy = Fxy[1]

    def update_theta(self, theta: float) -> None:
        """
        Increment the attribute `theta` of an `Agent` by a given amount `theta`.

        Parameters
        ----------
        theta : float
            The value to add to the attribute `theta`.
        """
        self.theta += theta
        self.theta = self.theta % (2 * pi)
        self.current_agent_big.rotate(np.rad2deg(theta))
        self.current_agent_big.rotate_body3D(np.rad2deg(theta))

    def update_torque(self, torque: float) -> None:
        """
        Increment the attribute `torque` of an `Agent` by a given amount `torque`.

        Parameters
        ----------
        torque : float
            The value to add to the attribute `torque`.
        """
        self.torque += torque

    def update_position(self, x: float, y: float) -> None:
        """
        Update the position of the current agent to the specified coordinates.

        Parameters
        ----------
        x : float
            Target x-coordinate in meters.
        y : float
            Target y-coordinate in meters.
        """
        agent_position: Point = self.current_agent_big.get_position()
        self.current_agent_big.translate(x * cst.M_TO_CM - agent_position.x, y * cst.M_TO_CM - agent_position.y)
        self.current_agent_big.translate_body3D(x * cst.M_TO_CM - agent_position.x, y * cst.M_TO_CM - agent_position.y, 0.0)
        agent_position_translated: Point = self.current_agent_big.get_position()
        self.x = agent_position_translated.x * cst.CM_TO_M
        self.y = agent_position_translated.y * cst.CM_TO_M


class Scenario:
    """Class representing the simulation scenario."""

    def __init__(self) -> None:
        """
        Initialize a Scenario instance with empty walls and agents.

        Attributes
        ----------
        walls : list[tuple[float,float]]
            A list of walls, where each wall is a list of (x, y) tuples representing wall points.
        totalwalls : int
            The total number of walls in the scenario.
        current_wallId : int
            The index of the currently active wall (for editing or drawing).
        agents : list
            A list of agents present in the scenario.
        current_agent_kivy_selected_id : int
            The index of the currently selected agent, or -1 if none is selected.
        """
        # Walls Variables
        self.walls: list[list[tuple[float, float]]] = []
        self.totalwalls: int = 0
        self.current_wallId: int = 0

        # List of agents
        self.agents: list[AgentKivy] = []
        self.nAgents: int = -1  # index of the current agent
        self.current_agent_kivy_selected_id: int = -1

        # Variable that says if data has been changed since last run of CrowdMechanics
        self.staticDataChange: bool = False

    def add_agent(self, x: int, y: int) -> None:
        """
        Add a new agent at the specified pixel coordinates.

        The agent's position is converted from pixel coordinates to world coordinates
        using the `pixel_density` factor, and the agent is appended to the `self.agents` list.
        The index of the newly added agent is stored in `self.nAgents`.

        Parameters
        ----------
        x : int
            The x-coordinate of the agent in pixels.
        y : int
            The y-coordinate of the agent in pixels.
        """
        self.agents.append(AgentKivy(float(x) / pixel_density, float(y) / pixel_density))
        self.nAgents = len(self.agents)
        self.current_agent_kivy_selected_id = self.nAgents - 1
        self.staticDataChange = True

    def add_NewWall(self, x0: int, y0: int) -> None:
        """
        Start a new wall at the specified pixel coordinates.

        Initializes a new wall by appending an empty list to `self.walls`, increments
        the total wall count, and adds the starting point (converted from pixel to world
        coordinates using `pixel_density`) to the new wall.

        Parameters
        ----------
        x0 : int
            The x-coordinate of the wall's starting point in pixels.
        y0 : int
            The y-coordinate of the wall's starting point in pixels.
        """
        self.walls.append([])
        self.totalwalls += 1
        self.walls[self.totalwalls - 1].append((float(x0) / pixel_density, float(y0) / pixel_density))

        self.staticDataChange = True

    def add_NewWallSec(self, x0: int, y0: int) -> None:
        """
        Add a new point (section) to the current wall at the specified pixel coordinates.

        Converts the given pixel coordinates to world coordinates using `pixel_density`
        and appends the point to the most recently created wall in `self.walls`.

        Parameters
        ----------
        x0 : int
            The x-coordinate of the new wall point in pixels.
        y0 : int
            The y-coordinate of the new wall point in pixels.
        """
        self.walls[self.totalwalls - 1].append((float(x0) / pixel_density, float(y0) / pixel_density))

        self.staticDataChange = True

    def get_last_WallPoint(self) -> tuple[float, float]:
        """
        Retrieve the last point added to the current wall.

        Returns
        -------
        tuple[float, float]
            The (x, y) coordinates of the last point added to the current wall.
        """
        return self.walls[self.totalwalls - 1][-1]

    def nextwall(self) -> None:
        """Start a new empty wall and increments the wall counter `self.totalwalls`."""
        self.walls.append([])
        self.totalwalls += 1

    def save(self) -> None:
        """
        Save the current geometry and agent data to XML files.

        Specifically, it creates:
            - `Geometry.xml` containing wall and geometry information, within the `static` directory.
            - `Agents.xml` containing agent properties,  within the `static` directory.
            - `AgentDynamics.xml` containing agent dynamic states,  within the `dynamic` directory.
        """
        # Walls
        with open(folderStatic / "Geometry.xml", "w", encoding="utf-8") as f:
            f.write(r'<?xml version="1.0" encoding="utf-8"?>' + "\n")
            f.write("<Geometry>\n")
            f.write(f'\t<Dimensions Lx="{Lx:.2f}" Ly="{Ly:.2f}"/>\n')
            for n, wall in enumerate(self.walls):
                f.write(f'\t<Wall Id="{n}" MaterialId="concrete">\n')
                for pt in wall:
                    f.write(f'\t\t<Corner Coordinates="{pt[0]:.2f},{pt[1]:.2f}"/>\n')
                f.write("\t</Wall>\n")
            f.write("</Geometry>")

        # Agents
        with open(folderStatic / "Agents.xml", "w", encoding="utf-8") as agentsFile:
            with open(folderDynamic / "AgentDynamics.xml", "w", encoding="utf-8") as dynamicsFile:
                agentsFile.write(r'<?xml version="1.0" encoding="utf-8"?>' + "\n")
                dynamicsFile.write(r'<?xml version="1.0" encoding="utf-8"?>' + "\n")
                agentsFile.write("<Agents>\n")
                dynamicsFile.write("<Agents>\n")
                for a, agent_kivy in enumerate(self.agents):
                    mass = agent_kivy.current_agent_big.measures.measures[cst.CommonMeasures.weight.name]
                    moment_of_inertia = agent_kivy.current_agent_big.measures.measures[cst.CommonMeasures.moment_of_inertia.name]
                    agentsFile.write(
                        f'\t<Agent Type="{agent_kivy.current_agent_big.agent_type.name}" Id="{a}" Mass="{mass:.2f}" '
                        f'MomentOfInertia="{moment_of_inertia:.2f}" FloorDamping="2.0" '
                        'AngularDamping="20.0">\n'
                    )
                    all_shape_params = agent_kivy.current_agent_big.shapes2D.get_additional_parameters()
                    delta_g_to_gi: dict[str, tuple[float, float]] = agent_kivy.current_agent_big.get_delta_GtoGi()
                    theta: float = agent_kivy.current_agent_big.get_agent_orientation()
                    delta_g_to_gi_rotated = fun.rotate_vectors(delta_g_to_gi, -theta)
                    for shape_name, shape_params in all_shape_params.items():
                        delta_g_to_gi_shape = delta_g_to_gi_rotated[shape_name]
                        agentsFile.write(
                            f'\t\t<Shape Type="{shape_params["type"]}" Radius="{float(np.round(shape_params["radius"], 3))}" '
                            f'MaterialId="{shape_params["material"]}" '
                            f'Position="{float(np.round(delta_g_to_gi_shape[0] * cst.CM_TO_M, 3))},'
                            f'{float(np.round(delta_g_to_gi_shape[1] * cst.CM_TO_M, 3))}"/>\n'
                        )

                    dynamicsFile.write(f'\t<Agent Id="{a}">\n')
                    # Write shapes too
                    dynamicsFile.write(
                        f'\t\t<Kinematics Position="{agent_kivy.x:.2f},{agent_kivy.y:.2f}" Velocity="{agent_kivy.vx:.3f},'
                        f'{agent_kivy.vy:.3f}" Theta="{agent_kivy.theta:.2f}" Omega="{agent_kivy.omega:.2f}"/>\n'
                    )
                    dynamicsFile.write(
                        f'\t\t<Dynamics Fp="{agent_kivy.Fx * BASE_VALUE_F:.2f},{agent_kivy.Fy * BASE_VALUE_F:.2f}" '
                        f'Mp="{agent_kivy.torque * BASE_VALUE_M:.2f}"/>\n'
                    )
                    agentsFile.write("\t</Agent>\n")
                    dynamicsFile.write("\t</Agent>\n")
                dynamicsFile.write("</Agents>")
            agentsFile.write("</Agents>")


class MyWidget(Widget):  # type: ignore[misc]
    """
    Class representing the main widget for the Kivy application.

    This class handles the drawing of the simulation environment, including walls,
    agents, and UI elements. It also manages user interactions such as mouse clicks
    and keyboard events.
    """

    def __init__(self) -> None:
        """
        Initialize the MyWidget instance with default state variables.

        Attributes
        ----------
        conf_save : bool | None
            Indicates whether the configuration has been saved.
        scenario : Scenario | None
            Reference to the current Scenario instance.
        pos_pressed : tuple[float,float] | None
            The (x, y) position of the last mouse or touch press.
        time_pressed : float | None
            The timestamp of the last mouse or touch press.
        current : int | None
            The current interaction mode or stage (e.g., wall creation, agent creation).
        drawing_walls : bool | None
            Indicates whether the user is currently drawing walls.
        """
        super().__init__()
        self.conf_save: bool | None = None
        self.scenario: Scenario | None = None
        self.pos_pressed: tuple[float, float] | None = None
        self.time_pressed: float | None = None
        self.current: int | None = None
        self.drawing_walls: bool | None = None
        self.modify_force_or_torque: int = 0

    def draw_cross(self, x: int, y: int, size: int) -> None:
        """
        Draw a cross centered at the specified pixel coordinates on the canvas.

        The cross consists of two diagonal lines intersecting at (x, y), each with a length determined by `size`.
        The lines are drawn using the `canvas` attribute, and their width is set to half of `size` (rounded).

        Parameters
        ----------
        x : int
            The x-coordinate of the cross center in pixels.
        y : int
            The y-coordinate of the cross center in pixels.
        size : int
            Half the length of each diagonal line of the cross.
        """
        int_x = int(x)
        int_y = int(y)
        with self.canvas:
            Line(points=(int_x - size, int_y - size, int_x + size, int_y + size), width=int(round(size / 2)))
            Line(points=(int_x + size, int_y - size, int_x - size, int_y + size), width=int(round(size / 2)))

    def draw_horizontal_line(self, y: float, size: float) -> None:
        """
        Draw a horizontal line at the specified y-coordinate on the canvas, that spans the whole canvas.

        Parameters
        ----------
        y : int
            The y-coordinate (in pixels) where the horizontal line will be drawn.
        size : int
            The thickness of the line.
        """
        with self.canvas:
            Line(points=[WS_X, int(y), 0, int(y)], width=int(round(size / 2)))

    def draw_vertical_line(self, x: float, size: float) -> None:
        """
        Draw a vertical line at the specified x-coordinate on the canvas, that spans the whole canvas.

        Parameters
        ----------
        x : int
            The x-coordinate (in pixels) where the vertical line will be drawn.
        size : int
            The thickness of the line.
        """
        with self.canvas:
            Line(points=[int(x), WS_Y, int(x), 0], width=int(round(size / 2)))

    def draw_arrow(self, xs: float, ys: float, xf: float, yf: float) -> None:
        """
        Draw an arrow from a starting point to an ending point on the canvas.

        The arrow consists of a main line connecting the start and end points, with an arrowhead
        at the endpoint. The arrowhead is formed by two short lines perpendicular to the direction
        of the main arrow.

        Parameters
        ----------
        xs : float
            The x-coordinate of the starting point (in pixels).
        ys : float
            The y-coordinate of the starting point (in pixels).
        xf : float
            The x-coordinate of the ending point (in pixels).
        yf : float
            The y-coordinate of the ending point (in pixels).
        """
        tx = xf - xs
        ty = yf - ys
        t_norm = np.sqrt(tx**2 + ty**2)
        tx /= t_norm
        ty /= t_norm
        tx1 = -tx - ty
        ty1 = -ty + tx
        tx2 = -tx + ty
        ty2 = -ty - tx

        with self.canvas:
            Line(points=(int(xs), int(ys), int(xf), int(yf)), width=2)
            Line(points=(int(xf), int(yf), int(xf) + int(10.0 * tx1), int(yf) + int(10.0 * ty1)), width=2)
            Line(points=(int(xf), int(yf), int(xf) + int(10.0 * tx2), int(yf) + int(10.0 * ty2)), width=2)

    def draw_grid(self) -> None:
        """
        Draw a grid on the canvas.

        The grid is rendered by drawing vertical and horizontal lines at regular intervals
        across the canvas. The grid color is set to a light gray. The spacing and extent
        of the grid are determined by the variables `dx`, `dy`, `Lx`, and `Ly`.
        Each grid line is drawn with a thickness of 1 pixel (since width=2 is divided by 2 in drawing line methods defined).
        """
        with self.canvas:
            Color(0.9, 0.9, 0.9, mode="bgr")
        for x in range(M1):
            self.draw_vertical_line(float(pixel_density * x * dx), 2)
        for y in range(M2):
            if y == 34 or y == 6:
                self.draw_horizontal_line(float(pixel_density * y * dy), 5)
            else:
                self.draw_horizontal_line(float(pixel_density * y * dy), 2)

    def draw_confSave(self) -> None:
        """Display a confirmation message on the center of the canvas when the configuration is saved."""
        with self.canvas:
            if self.conf_save:
                Color(0, 0, 0, mode="bgr")
                label = CoreLabel(text="Configuration Saved!", font_size=22)
                label.refresh()
                Rectangle(pos=(WS_X / 2.0 - 125, WS_Y - 100), size=(250, 40), texture=label.texture)

                label2 = CoreLabel(text="Type q to quit", font_size=11)
                label2.refresh()
                Rectangle(pos=(WS_X / 2.0 - 63, WS_Y - 125), size=(125, 20), texture=label2.texture)

    def draw_buttons(self) -> None:
        """Draw stage instructions on the canvas."""
        with self.canvas:
            Color(0, 0, 0, 1, mode="bgra")
            if self.current == 0:
                label = CoreLabel(text="Stage 1: Create walls (press SPACE to move on)", font_size=30)
                label.refresh()
                Rectangle(pos=(200, WS_Y - 50), size=(450, 60), texture=label.texture)
            elif self.current == 1:
                label = CoreLabel(text="Stage 2: Spawn one agent (press SPACE to move on)", font_size=30)
                label.refresh()
                Rectangle(pos=(200, WS_Y - 50), size=(450, 60), texture=label.texture)
            elif self.current == 2:
                label = CoreLabel(text="Stage 3: Run simulation (press 'r')", font_size=30)
                label.refresh()
                Rectangle(pos=(200, WS_Y - 50), size=(450, 60), texture=label.texture)

            if self.current == -1:
                Color(1, 0, 0, mode="bgr")
                label = CoreLabel(text="But there are no agents!", font_size=20)
                label.refresh()
                Rectangle(pos=(200, 0), size=(450, 60), texture=label.texture)

            col_bottons = np.ones(5) * 0.3
            col_bottons[self.current] = 1

            Color(0, 0, 0, col_bottons[0], mode="bgra")
            label = CoreLabel(text="Set walls (w)", font_size=20)
            label.refresh()
            Rectangle(pos=(WS_X - 150, WS_Y - 50), size=(100, 40), texture=label.texture)

            Color(0, 0, 1, col_bottons[1], mode="bgra")
            label = CoreLabel(text="Spawn agent (a)", font_size=20)
            label.refresh()
            Rectangle(pos=(WS_X - 150, WS_Y - 100), size=(100, 40), texture=label.texture)

    def draw_agents(self) -> None:
        """
        Render all agents on the canvas with visual indicators.

        For each agent, this method draws:
            - A polygon representing the agent's shape
            - An arrow showing the propulsion force vector applied to the agent

        The current agent (defined by `self.scenario.current_agent_kivy_id`) is drawn with full opacity,
        while others are rendered at 30% opacity.

        Raises
        ------
        ValueError
            If `self.scenario` is not initialized.
        """
        if self.scenario is None:
            raise ValueError("Scenario is not initialized")

        with self.canvas:
            for cpt_agent, current_agent_kivy in enumerate(self.scenario.agents):
                geometric_agent = current_agent_kivy.current_agent_big.shapes2D.get_geometric_shape()
                agent_position: Point = current_agent_kivy.current_agent_big.get_position()
                geometric_agent_in_pixels = affin.scale(
                    geometric_agent, cst.CM_TO_M * pixel_density, cst.CM_TO_M * pixel_density, origin=agent_position
                )
                agent_position_in_pixels = affin.scale(
                    agent_position, cst.CM_TO_M * pixel_density, cst.CM_TO_M * pixel_density, origin=(0.0, 0.0)
                )
                new_agent_in_pixels = affin.translate(
                    geometric_agent_in_pixels,
                    agent_position_in_pixels.x - agent_position.x,
                    agent_position_in_pixels.y - agent_position.y,
                )
                contours = shapely_to_kivy_contours(new_agent_in_pixels)
                tess = Tesselator()
                for contour in contours:
                    tess.add_contour(contour)
                tess.tesselate()
                with self.canvas:
                    alphaAgent = 1.0
                    alphaForce = 0.5
                    if self.current == 1:
                        if cpt_agent != self.scenario.current_agent_kivy_selected_id:
                            alphaAgent *= 0.25
                            alphaForce *= 0.25
                    Color(rc[cpt_agent][0], rc[cpt_agent][1], rc[cpt_agent][2], alphaAgent, mode="bgra")
                    for vertices, indices in tess.meshes:
                        Mesh(vertices=vertices, indices=indices, mode="triangle_fan")

                Color(1, 0, 0, alphaForce, mode="bgra")
                self.draw_arrow(
                    pixel_density * current_agent_kivy.x,
                    pixel_density * current_agent_kivy.y,
                    pixel_density * (current_agent_kivy.x + current_agent_kivy.Fx / (N_PIXELS_ONE * 0.5)),
                    pixel_density * (current_agent_kivy.y + current_agent_kivy.Fy / (N_PIXELS_ONE * 0.5)),
                )

    def draw_walls(self) -> None:
        """
        Draw all walls on the canvas as connected line segments.

        Raises
        ------
        ValueError
            If  the scenario is not initialized.
        """
        if self.scenario is None:
            raise ValueError("Scenario is not initialized")

        with self.canvas:
            for _, cw in enumerate(self.scenario.walls):
                Color(0, 0, 0, 1, mode="bgra")
                if len(cw) >= 2:
                    for i in range(len(cw) - 1):
                        Line(
                            points=(
                                pixel_density * cw[i][0],
                                pixel_density * cw[i][1],
                                pixel_density * cw[i + 1][0],
                                pixel_density * cw[i + 1][1],
                            ),
                            width=3,
                        )

    def draw_agent_values(self) -> None:
        """
        Draw agent state values and force/torque information on the canvas.

        Renders a UI panel displaying:
        - Agent ID
        - Position (x, y) and orientation (θ)
        - Linear velocities (vx, vy) and angular velocity (ω)
        - Forces (Fx, Fy) and torque (M)
        - Force values change color based on modification mode

        Requires a valid scenario and agent selection. Draws nothing if:
        - Scenario is not initialized
        - Current timestep is 0
        - No agents exist in the scenario

        Raises
        ------
        ValueError
            If the scenario has not been properly initialized.
        """
        if self.scenario is None:
            raise ValueError("Scenario is not initialized")
        if self.current == 0:
            return
        if self.scenario.nAgents == -1:
            return
        agent = self.scenario.agents[self.scenario.current_agent_kivy_selected_id]
        with self.canvas:
            Color(0, 0, 0, 1, mode="bgra")
            Line(points=(50, 100, WS_X - 50, 100), width=1)
            label = CoreLabel(text=f"Agent {self.scenario.current_agent_kivy_selected_id:d}", font_size=24)
            label.refresh()
            Rectangle(pos=(50, 110), size=(100, 40), texture=label.texture)
            label = CoreLabel(text=f"x: {agent.x:.2f} m", font_size=20)
            label.refresh()
            Rectangle(pos=(50, 70), size=(100, 20), texture=label.texture)
            label = CoreLabel(text=f"y: {agent.y:.2f} m", font_size=20)
            label.refresh()
            Rectangle(pos=(50, 40), size=(100, 20), texture=label.texture)
            label = CoreLabel(text=f"θ: {agent.theta:.2f} rad", font_size=20)
            label.refresh()
            Rectangle(pos=(50, 10), size=(100, 20), texture=label.texture)
            label = CoreLabel(text=f"vx: {agent.vx:.2f} m/s", font_size=20)
            label.refresh()
            Rectangle(pos=(200, 70), size=(100, 20), texture=label.texture)
            label = CoreLabel(text=f"vy: {agent.vy:.2f} m/s", font_size=20)
            label.refresh()
            Rectangle(pos=(200, 40), size=(100, 20), texture=label.texture)
            label = CoreLabel(text=f"ω: {agent.omega:.2f} rad/s", font_size=20)
            label.refresh()
            Rectangle(pos=(200, 10), size=(100, 20), texture=label.texture)

            if self.modify_force_or_torque == 0:
                Color(1, 0, 0, mode="bgr")
            label = CoreLabel(text=f"Fx: {agent.Fx * BASE_VALUE_F:.2f} N", font_size=20)
            label.refresh()
            Rectangle(pos=(400, 60), size=(200, 40), texture=label.texture)
            label = CoreLabel(text=f"Fy: {agent.Fy * BASE_VALUE_F:.2f} N", font_size=20)
            label.refresh()
            Rectangle(pos=(400, 20), size=(200, 40), texture=label.texture)

            if self.modify_force_or_torque == 0:
                Color(0, 0, 0, mode="bgr")
            else:
                Color(1, 0, 0, mode="bgr")
            label = CoreLabel(text=f"M: {agent.torque * BASE_VALUE_M:.2f} Nm", font_size=20)
            label.refresh()
            Rectangle(pos=(700, 40), size=(200, 40), texture=label.texture)

    def redraw(self) -> None:
        """
        Redraw the entire canvas, updating all visual elements.

        This method clears the current canvas and sequentially redraws all visual components,
        including the grid, UI buttons, agents, walls, and any configuration save messages.
        """
        self.canvas.clear()
        self.draw_grid()
        self.draw_buttons()
        self.draw_agents()
        self.draw_walls()
        self.draw_confSave()
        self.draw_agent_values()

    def isCliskOnAgent(self) -> bool:
        """
        Check if the last mouse click was on the central disk of the current agent.

        Returns True if the coordinates of the last pressed position (`self.pos_pressed`) are within
        the middle disk of the current agent. The agent's disk is centered at
        (`agent.x`, `agent.y`) and has a radius of `radius`, both scaled by `pixel_density`.

        Returns
        -------
        bool
            True if the last click was within the agent's disk area, False otherwise.
        """
        if self.pos_pressed is None:
            raise ValueError("Position pressed is not initialized")
        if self.scenario is None:
            raise ValueError("Scenario is not initialized")

        cpt_agent = 0
        for agent in self.scenario.agents:
            # agent_kivy = self.scenario.agents[self.scenario.current_agent_kivy_selected_id]
            if (
                np.sqrt((self.pos_pressed[0] - pixel_density * agent.x) ** 2 + (self.pos_pressed[1] - pixel_density * agent.y) ** 2)
                <= pixel_density * agent.current_agent_big.shapes2D.get_additional_parameters()["disk2"]["radius"]
            ):
                self.scenario.current_agent_kivy_selected_id = cpt_agent
                return True
            cpt_agent += 1
        return False

    def on_touch_up(self, touch: kivy.input.motionevent.MotionEvent) -> None:
        """
        Handle touch release events (with the mouse) for wall/agent creation and interaction.

        Parameters
        ----------
        touch : kivy.input.motionevent.MotionEvent
            The touch event object containing position and button information.

        Notes
        -----
        Behavior depends on the current interaction mode (`self.current`):
            - **Mode 0 (Wall Creation)**:
                - Right click: Stops drawing walls
                - Left click: Starts a new wall or adds points to existing walls
            - **Mode 1 (Agent Interaction)**:
                - Torque button click: Applies torque based on press duration
                - Agent click: Rotates agent based on press duration
                - Left click: Spawns new agent
                - Other clicks: Sets force target for current agent
        """
        if self.scenario is None:
            raise ValueError("Scenario is not initialized")
        if self.time_pressed is None:
            raise ValueError("Time pressed is not initialized")

        x, y = touch.pos

        with self.canvas:
            if self.current == 0:  # New wall
                (x1, y1) = get_closest_node(x, y)

                if touch.button == "right":
                    self.drawing_walls = False
                else:
                    if not self.drawing_walls:
                        self.scenario.add_NewWall(x1, y1)
                        self.drawing_walls = True
                    else:
                        self.scenario.add_NewWallSec(x1, y1)
                        Color(0, 0, 0, mode="bgr")
                        (x0, y0) = self.scenario.get_last_WallPoint()
                        Line(points=(x0, y0, x1, y1), width=3)

            elif self.current == 1:  # New agent
                if (
                    self.scenario.nAgents > 0
                    and self.time_pressed > 0
                    and self.modify_force_or_torque == 1
                    and not self.isCliskOnAgent()
                ):
                    agent_kivy = self.scenario.agents[self.scenario.current_agent_kivy_selected_id]
                    intensity = 0.5 * (time.time() - self.time_pressed)
                    if touch.button == "right":
                        intensity *= -1.0
                    agent_kivy.update_torque(intensity)

                elif self.scenario.nAgents > 0 and self.time_pressed > 0 and self.isCliskOnAgent():
                    self.redraw()
                    agent_kivy = self.scenario.agents[self.scenario.current_agent_kivy_selected_id]
                    intensity = 0.5 * (time.time() - self.time_pressed)
                    if touch.button == "right":
                        intensity *= -1.0
                    agent_kivy.update_theta(intensity)

                elif touch.button == "left":
                    self.scenario.add_agent(x, y)
                    Color(0, 0, 1, mode="bgr")

                elif self.scenario.nAgents > 0:
                    agent_kivy = self.scenario.agents[self.scenario.current_agent_kivy_selected_id]
                    F_norm = 2.0 * (time.time() - self.time_pressed) if self.time_pressed > 0 else 1.0
                    F_norm /= np.sqrt((x / pixel_density - agent_kivy.x) ** 2 + (y / pixel_density - agent_kivy.y) ** 2)
                    agent_kivy.target_force = (
                        F_norm * (x / pixel_density - agent_kivy.x),
                        F_norm * (y / pixel_density - agent_kivy.y),
                    )

        self.time_pressed = -1
        self.canvas.clear()
        self.redraw()

    def mouse_pos(self, window: kivy.core.window.Window, touch: kivy.input.motionevent.MotionEvent) -> None:  # pylint: disable=unused-argument
        """
        Handle mouse position updates.

        This method updates the canvas periodically (every ~0.2 seconds) and draws:
            - Temporary wall segments during wall creation (mode 0)
            - Force/torque preview lines during force torque setting (mode 1)

        Parameters
        ----------
        window : kivy.core.window.Window
            The Kivy window object (unused in this implementation but required by Kivy's event system).
        touch : kivy.input.motionevent.MotionEvent
            The mouse position coordinates in pixel space. Typically contains [x, y] values.
        """
        if self.scenario is None:
            raise ValueError("Scenario is not initialized")
        if self.time_pressed is None:
            raise ValueError("Time pressed is not initialized")
        if self.pos_pressed is None:
            raise ValueError("Position pressed is not initialized")

        if not int(50 * time.time()) % 5 == 1:
            return

        self.redraw()
        with self.canvas:
            if self.current == 0:
                if self.drawing_walls:
                    Color(0, 0, 0, mode="bgr")
                    Lwp = self.scenario.get_last_WallPoint()
                    Line(points=(Lwp[0] * pixel_density, Lwp[1] * pixel_density, touch[0], touch[1]), width=3)

            elif self.time_pressed > 0:
                Color(rc[1][0], rc[1][1], rc[1][2], mode="bgr")
                Line(points=(self.pos_pressed[0], self.pos_pressed[1], touch[0], touch[1]), width=3)

    def on_touch_down(self, touch: kivy.input.motionevent.MotionEvent) -> None:
        """
        Handle mouse press events, such as the initiation of a touch event or mouse click.

        Records the time and position of the mouse press for later use. If the right mouse button is pressed,
        it also stops the wall-drawing mode.

        Parameters
        ----------
         touch : kivy.input.motionevent.MotionEvent
             The touch event object containing position (`x`, `y`) and button information.
        """
        self.time_pressed = time.time()
        self.pos_pressed = (touch.x, touch.y)
        if touch.button == "right":
            self.drawing_walls = False

    def initialise(self) -> None:
        """
        Initialize the simulation environment and UI state.

        Notes
        -----
        - Sets `self.current` to 0 (wall creation mode).
        - Creates a new `Scenario` instance and assigns it to `self.scenario`.
        - Resets `self.pos_pressed` and `self.time_pressed` to invalid values.
        - Draws the initial grid and UI buttons.
        """
        self.current = 0  # 0: wall 1: agent 2: Simulate!
        self.scenario = Scenario()
        self.pos_pressed = (-1, -1)
        self.time_pressed = -1
        self.drawing_walls = False
        self.conf_save = False
        Window.bind(mouse_pos=self.mouse_pos)
        self.draw_grid()
        self.draw_buttons()


class MyApp(App):  # type: ignore[misc]
    """
    Main application class for the Kivy simulation interface.

    Attributes
    ----------
    widget : Widget | None
        Reference to the main application widget. Initialized as None and set during the build process.
    """

    def __init__(self) -> None:
        """
        Initialize the MyApp application instance.

        Attributes
        ----------
        widget : Widget | None
            Reference to the main application widget. Initialized as None and set during the build process.
        """
        super().__init__()
        self.widget: Widget | None = None

    def get_number_from_popup(self) -> None:
        """Display a popup dialog to prompt the user for input."""
        textinput = TextInput(multiline=False)
        popup = Popup(title="Enter ellipse orientation in degrees", content=textinput, size_hint=(None, None), size=(400, 200))

        def on_text_enter(instance: TextInput) -> None:
            """
            Handle the Enter key press event on the text input.

            Parameters
            ----------
            instance : TextInput
                The text input widget instance.
            """
            if not isinstance(self.widget, MyWidget):
                raise ValueError("Widget is not initialized")
            if not isinstance(self.widget.scenario, Scenario):
                raise ValueError("Scenario is not initialized")
            if self.widget.scenario is None:
                raise ValueError("Scenario is not initialized")
            try:  # it wait until the user enter a number, then the popup is dismissed (closed)
                popup.dismiss()
            except ValueError:
                instance.text = ""
                instance.hint_text = "Please enter a valid number"
            popup.dismiss()

        textinput.bind(on_text_validate=on_text_enter)  # pylint: disable=no-member
        popup.open()

    def _handle_default_case(self, files_input: Any, folder_dynamic: Path) -> None:  # pylint: disable=unused-argument
        """
        Handle the default case for widget state changes.

        This function:
        1. Resets widget state if no agents exist
        2. Forces reload of static data if changed
        3. Saves scenario and runs mechanical simulation
        4. Updates agent kinematics from XML output
        5. Triggers widget redraw

        Parameters
        ----------
        files_input : Any
            Input files structure for mechanical simulation (type depends on external library).
        folder_dynamic : Path
            Path to directory containing dynamic simulation files.

        Raises
        ------
        FileNotFoundError
            If AgentDynamics.xml is not found in folder_dynamic.
        """
        if self.widget is None:
            raise ValueError("Widget is not initialized")
        if len(self.widget.scenario.agents) == 0:
            self.widget.current = -1
            return

        # If the user has changed the geometry or the agents, we force the loadStaticData variable to be true
        # in the library, so it will re-read the static files.
        if self.widget.scenario.staticDataChange:
            loadStaticData = ctypes.c_bool.in_dll(mechanicalLayer, "loadStaticData")
            loadStaticData.value = True
            self.widget.scenario.staticDataChange = False

        # Accordingly, we re-save everything, ie recreate all files
        self.widget.scenario.save()

        mechanicalLayer.CrowdMechanics(filesInput)
        # Read from AgentDynamics output file to update agents
        dynamicsFile = Path(folderDynamic / "AgentDynamics.xml")
        XMLtree = ET.parse(dynamicsFile)
        agentsTree = XMLtree.getroot()
        for a in range(len(agentsTree)):
            agent = self.widget.scenario.agents[a]
            kinematics = agentsTree[a].find("Kinematics")
            if kinematics is None or kinematics.attrib is None:
                raise ValueError(f"Kinematics for agent {a} is missing or has no attributes")
            for key, value in kinematics.attrib.items():
                if key == "Position":
                    vector = value.split(",")
                    agent.update_position(float(vector[0]), float(vector[1]))
                elif key == "Velocity":
                    vector = value.split(",")
                    agent.vx = float(vector[0])
                    agent.vy = float(vector[1])
                elif key == "Theta":
                    agent.update_theta(float(value) - agent.theta)
                elif key == "Omega":
                    agent.omega = float(value)
        self.widget.redraw()

    def key_action(self, keyboard: object, keycode0: int, keycode1: int, text: str, modifiers: list[str]) -> None:  # pylint: disable=unused-argument
        """
        Handle keyboard input events for controlling the application workflow.

        Parameters
        ----------
        keyboard : object
            Kivy keyboard reference (unused but required by Kivy event system).
        keycode0 : int
            Native keycode (unused but required by Kivy event system).
        keycode1 : int
            Kivy keycode (unused but required by Kivy event system).
        text : str
            The character representation of the pressed key.
        modifiers : list
            Active modifier keys (e.g., shift, ctrl) - unused but required by Kivy event system.

        Notes
        -----
        Here are the key bindings:
            - 'a' : Switch to agent creation mode
            - 'w' : Switch to wall creation mode
            - 'f' : Set force modification mode (only in agent creation mode)
            - 't' : Set torque modification mode (only in agent creation mode)
            - 'r' : Run the simulation (if in simulation stage)
            - ' ' : Space - Advance to next interaction stage
            - 's' : Save current configuration
            - 'q' : Quit the application

        The stage progression (space bar) cycles through modes: walls -> agents -> simulation
        """
        if self.widget is None:
            raise ValueError("Widget is not initialized")

        if text == "a":  # Spawn agent
            self.widget.current = 1
            self.widget.drawing_walls = False
            self.widget.redraw()

        elif text == "w":  # Set walls
            self.widget.current = 0
            self.widget.drawing_walls = False
            self.widget.scenario.current_wallId = 0
            self.widget.redraw()

        elif text == "s":  # Save configuration
            self.widget.conf_save = True
            self.widget.draw_confSave()
            self.widget.scenario.save()

        elif text == "f" and self.widget.current == 1:  # Set force modification mode
            self.widget.modify_force_or_torque = 0
            self.widget.redraw()
        elif text == "t" and self.widget.current == 1:  # Set torque modification mode
            self.widget.modify_force_or_torque = 1
            self.widget.redraw()

        elif text == " ":  # Space bar, move to next stage
            self.widget.conf_save = True
            if self.widget.current < 2:
                self.widget.current += 1
                self.widget.draw_confSave()
                self.widget.scenario.save()
            else:
                self.widget.current = (self.widget.current + 1) % 3

        elif text == "r":  # Run simulation
            match self.widget.current:
                case 0:
                    self.widget.drawing_walls = False
                    self.widget.scenario.current_wallId = 0
                    self.widget.redraw()
                case 1:
                    self.widget.drawing_walls = False
                    self.widget.redraw()
                case _:
                    self._handle_default_case(filesInput, folderDynamic)

        elif text == "q":  # Quit
            sys.exit()

    def build(self) -> Widget:
        """
        Build and initialize the main application widget.

        Returns
        -------
        Widget
            The main application widget (`self.widget`) that serves as the root of the UI.

        Notes
        -----
        - Sets the window background color to white `(1, 1, 1, 1)` (opaque white).
        - Sets the window size using the global constants `WS_X` and `WS_Y`.
        - Binds the `on_key_down` event of the window to `self.key_action` for keyboard input handling.
        """
        Window.clearcolor = (1, 1, 1, 1)
        Window.size = (WS_X, WS_Y)
        self.title = "Crowd simulator"
        self.widget = MyWidget()
        self.widget.initialise()

        Window.bind(on_key_down=self.key_action)
        return self.widget


if __name__ == "__main__":
    # Set Kivy configuration to use the mouse
    Config.set("input", "mouse", "mouse,multitouch_on_demand")

    # Load the CrowdMechanics library into ctypes
    libname = str(Path().absolute().parent.parent / "src" / "mechanical_layer" / "build" / "libCrowdMechanics.dylib")
    mechanicalLayer = ctypes.CDLL(libname)
    files = [
        b"./Parameters.xml",
        b"Materials.xml",
        b"Geometry.xml",
        b"Agents.xml",
        b"AgentDynamics.xml",
    ]
    nFiles = len(files)
    filesInput = cast(list[ctypes.c_char_p | bytes | None], (ctypes.c_char_p * nFiles)())
    filesInput[:] = files

    MyApp().run()
