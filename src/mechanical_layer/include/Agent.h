/*
    Copyright  2025  Institute of Light and Matter, CNRS UMR 5306, University Claude Bernard Lyon 1
    Contributors: Oscar DUFOUR, Maxime STAPELLE, Alexandre NICOLAS

    This software is a computer program designed to generate a realistic crowd from anthropometric data and
    simulate the mechanical interactions that occur within it and with obstacles.

    This software is governed by the CeCILL-B license under French law and abiding by the rules of distribution
    of free software.  You can  use, modify and/ or redistribute the software under the terms of the CeCILL-B
    license as circulated by CEA, CNRS and INRIA at the following URL "http://www.cecill.info".

    As a counterpart to the access to the source code and  rights to copy, modify and redistribute granted by
    the license, users are provided only with a limited warranty  and the software's author,  the holder of the
    economic rights,  and the successive licensors  have only  limited liability.

    In this respect, the user's attention is drawn to the risks associated with loading,  using,  modifying
    and/or developing or reproducing the software by the user in light of its specific status of free software,
    that may mean  that it is complicated to manipulate,  and  that  also therefore means  that it is reserved
    for developers  and  experienced professionals having in-depth computer knowledge. Users are therefore
    encouraged to load and test the software's suitability as regards their requirements in conditions enabling
    the security of their systems and/or data to be ensured and,  more generally, to use and operate it in the
    same conditions as regards security.

    The fact that you are presently reading this means that you have had knowledge of the CeCILL-B license and that
    you accept its terms.
*/

#ifndef SRC_MECHANICAL_LAYER_INCLUDE_AGENT_H_
#define SRC_MECHANICAL_LAYER_INCLUDE_AGENT_H_

#include "Global.h"

struct Agent
/**
 * @brief Class representing an agent in the simulation.
 *
 * This class defines the properties and behaviors of an agent, such as its position, velocity, and shape.
 * Agents can interact with each other and navigate through the environment based on a driving force.
 */
{
    const unsigned _id;                        ///< Agent id
    const double _mass;                        ///<  Mass
    const double _moi;                         ///<  Moment of inertia
    const std::vector<unsigned> _ids_shapes;   ///<  List of ids of the shapes of the agent
    const double _radius;                      ///<  Equivalent radius for repulsive force
    const unsigned _nb_shapes;                 ///< Number of shapes of the agent
    std::vector<double2> _delta_gtos;   ///<  List of vector from the center of mass G to the center of each physical shape (disc)

    const std::vector<double> _radius_shapes;   ///<  The radii of the agent's shapes
    /// The initial value of the agent's orientation, derived from the relative positions of its shapes in the Agents XML file.
    const double _theta_init;
    double _x;           ///< x-component of the center of mass
    double _y;           ///< y-component of the center of mass
    double _theta;       ///< Orientation of the agent
    double _vx;          ///< x-component of the velocity of the center of mass
    double _vy;          ///< y-component of the velocity of the center of mass
    double _w;           ///<  Angular velocity of the agent
    double _vx_des;      ///<  x-component of the desired velocity of the agent
    double _vy_des;      ///<  y-component of the desired velocity of the agent
    double _w_des;       ///<  Desired angular velocity of the agent
    double _theta_des;   ///<  Desired orientation of the agent (orientation of the desired velocity)

    double2 _v_des;                                               ///< Norm (N2) of the desired velocity
    std::list<unsigned> _neighbours;                              ///<  List of neighbours
    std::list<std::pair<unsigned, unsigned>> _neighbours_walls;   ///<  List of neighbouring walls

    /*  Constructor for the class   */
    Agent(unsigned ID, std::vector<unsigned> Ids_shapes, unsigned nb_shapes, const std::vector<double2>& delta_gtos,
          const std::vector<double>& radius_shapes, double theta_body_init, double mass, double moi);
    ~Agent();

    void move();
    /**
     * @brief The method gets the current position of the agent
     *
     * @returns The position in cartesian coordinates as a double2
     */
    inline double2 get_r() { return {_x, _y}; }
    /**
     * @brief The method gets the current velocity of the agent
     *
     * @returns The velocity in cartesian coordinates as a double2
     */
    inline double2 get_v() { return {_vx, _vy}; }
    std::vector<double2> get_delta_gtos();
};

#endif   // SRC_MECHANICAL_LAYER_INCLUDE_AGENT_H_
