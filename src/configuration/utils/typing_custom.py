"""Custom type definitions."""

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

from typing import Literal, TypeAlias

from shapely.geometry import MultiPolygon, Polygon

#: Represents biological sex categories.
Sex: TypeAlias = Literal[
    "male",
    "female",
]

#: Represents different types of agents in the system.
AgentType: TypeAlias = Literal[
    "pedestrian",
    "bike",
    "custom",
]

#: Represents the parts of an agent (e.g., physical dimensions).
AgentPart: TypeAlias = Literal[
    "chest_depth",
    "bideltoid_breadth",
    "height",
    "sex",
    "wheel_width",
    "total_length",
    "handlebar_length",
    "top_tube_length",
]

#: Represents different types of shapes used in geometry.
ShapeType: TypeAlias = Literal[
    "disk",
    "rectangle",
    "polygon",
]

#: Represents common materials used in crowd simulations.
MaterialType: TypeAlias = Literal[
    "concrete",
    "human_naked",
    "human_clothes",
]

#: Represents supported backup data formats.
BackupDataType: TypeAlias = Literal[
    "pickle",
    "xml",
]

#: Represents the structure of shape-related data.
ShapeDataType: TypeAlias = (
    dict[str, dict[str, ShapeType | MaterialType | float]]
    | dict[str, dict[str, ShapeType | MaterialType | float | Polygon | MultiPolygon]]
)

#: Represents the structure of a crowd-related data.
StaticCrowdDataType: TypeAlias = dict[str, dict[str, dict[str, AgentType | float | int | ShapeDataType]]]

#: Represents the structure of dynamic crowd-related data.
DynamicCrowdDataType: TypeAlias = dict[
    str,  # Top-level key ("Agents")
    dict[
        str,  # Keys inside "Agents" ("Agent0", "Agent1", ...)
        dict[
            str,  # Keys inside each agent ("id", "Kinematics", "Dynamics")
            int | dict[str, float],
        ],
    ],
]

#: Represents the structure of geometry-related data.
GeometryDataType: TypeAlias = dict[
    str,  # Top-level key ("Geometry")
    dict[
        str,  # Keys inside "Geometry" ("Dimensions", "Wall")
        dict[str, float]
        | dict[
            str,  # Keys inside "Wall" ("Wall0", "Wall1", ...)
            dict[str, int | MaterialType | dict[str, dict[str, float]]],
        ],
    ],
]

#: Represents the intrinsic properties of each material.
IntrinsicMaterialDataType = dict[str, dict[str, int | str | float]]

#: Represents the properties associated with each pair of material.
PairMaterialsDataType = dict[str, dict[str, int | float]]

#: Represents the structure of material-related data.
MaterialsDataType = dict[
    str,  # Top-level key ("Material")
    dict[
        str,  # Keys inside "Material" ("Intrinsic", "Binary")
        IntrinsicMaterialDataType | PairMaterialsDataType,
    ],
]

#: Represents the structure of interaction-related data.
InteractionsDataType: TypeAlias = dict[
    str,  # Top-level key ("Interactions")
    dict[
        str,  # Keys inside "Interactions" ("Agent0", "Agent1", ...)
        dict[
            str,  # Keys inside each agent ("Id", "NeighbouringAgents")
            int
            | dict[
                str,  # Keys inside "NeighbouringAgents" ("Id", "Interactions"
                int
                | dict[
                    str,  # Keys inside "Interactions" ("Interaction_0_0", "Interaction_0_1", ...)
                    dict[
                        str,  # Keys inside each interaction ("ParentShapeId", "ChildShapeId", "Ftx", ...)
                        int | tuple[float, float],
                    ],
                ],
            ],
        ],
    ],
]
