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

#ifndef SRC_MECHANICAL_LAYER_INCLUDE_MECHANICALLAYER_H_
#define SRC_MECHANICAL_LAYER_INCLUDE_MECHANICALLAYER_H_

#include "Agent.h"
#include "Global.h"

//  Helper list to make indices explicit
#if !defined(DOXYGEN_SHOULD_SKIP_THIS)
enum __attribute__((__packed__)) interactionsOutput_e
{
    SLIP = 0,
    FORCE_ORTHO = 1,
    FORCE_TAN = 2,
};
#endif   // DOXYGEN_SHOULD_SKIP_THIS
struct MechanicalLayer
/**
 * @brief Class representing the mechanical behavior of a crowd of pedestrians.
 *
 * This class handles the mechanical interactions between pedestrians in a crowd.
 * It keeps track of the positions, velocities, orientations, and forces acting on each pedestrian.
 * The class also provides methods for updating the positions and velocities of the pedestrians
 * and saving the configuration to a file.
 */
{
   private:
    unsigned nb_active_agents;      //  Number of mechanically active agens
    unsigned nb_active_shapes;      //  Number of pedestrians (each pedestrian is a collection of active agents)
    std::vector<double2> vgn;       //  Velocity of the center of mass (CM) of each pedestrian at t
    std::vector<double2> vgnp1;     //  Velocity of the CM of each pedestrian at t+dt
    std::vector<double2> rgcomp;    //  Initial positions of all the components of the pedestrians
    std::vector<double2> rgn;       //  Positions of the CM of each pedestrian at t
    std::vector<double2> rgnp1;     //  Positions of the CM of each pedestrian at t+dt
    std::vector<double2> delta;     //  Difference between position of the CM of each component and
                                    //  the CM of their associated pedestrian
    std::vector<double> thetn;      //  Orientation wrt x-axis at t
    std::vector<double> thetnp1;    //  Orientation wrt x-axis at t+dt
    std::vector<double> wn;         //  Angular velocity at t
    std::vector<double> wnp1;       //  Angular velocity at t+dt
    std::vector<double> wdesired;   //  Desired orientation wrt x-axis
                                    //  Forces have the dimension of an acceleration
    std::vector<double2> Fp;        //  Propelling force v_des/tau_mech
    std::vector<double2> Forthon;   //  Orthogonal force (hertz) wrt contact surface at time t
    std::vector<double2> Ftn;       //  Tangential force wrt contact surface at time t
    std::vector<double> taun;       //  Torque at time t (moment projected on z-axis) expressed at the CM
    std::vector<std::list<int>> neighbours;
    std::vector<unsigned> active_shapeIDagent;         //  Pedestrian id of each shape
    std::vector<unsigned> active_shapeIDshape_crowd;   //  Shape id of each pedestrian
    std::vector<double> radius;                        //  Radius off all shapes of actives agents
    std::vector<unsigned> size_agents;
    std::map<unsigned, unsigned> agentIds;
    std::vector<unsigned> agentActiveIds;
    std::vector<std::vector<unsigned>> neighbours_shape;
    std::vector<unsigned> agentIDshape;
    std::vector<double> masses;
    std::vector<double> mois;
    std::vector<double2> damping;

    //  Tangential relative displacement when in contact
    std::map<std::pair<unsigned, unsigned>, double2> slip;
    std::map<std::tuple<unsigned, int, int>, double2> slip_wall;

    //  For output purposes: the following variables will contain:
    //    - a copy of slip
    //    - fortho from shape to shape
    //    - ft from shape to shape
    std::map<std::pair<unsigned, unsigned>, std::array<double2, 3>> interactionsOutput;
    std::map<std::tuple<unsigned, int, int>, std::array<double2, 3>> interactionsOutputWall;

    std::tuple<double2, double2, double> get_interactions(unsigned cpt_shape, bool AtTimen);
    void loop();
    //  AgentInteractions is an input and output file (ie "dynamic") of this process
    int readInteractionsInputFile(const std::string& interactionsFile);
    std::pair<bool, bool> existsContacts();   //  Do contacts exist?
    void generateInteractionsOutputFile(const std::string& interactionsFile, const std::pair<bool, bool>& exists);

   public:
    /// Constructor for the MechanicalLayer class.
    explicit MechanicalLayer(std::list<Agent*>& mech_active_agents);
    /// Destructor for the MechanicalLayer class.
    ~MechanicalLayer();
};

#endif   // SRC_MECHANICAL_LAYER_INCLUDE_MECHANICALLAYER_H_"
