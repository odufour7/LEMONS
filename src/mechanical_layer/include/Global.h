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

#ifndef SRC_MECHANICAL_LAYER_INCLUDE_GLOBAL_H_
#define SRC_MECHANICAL_LAYER_INCLUDE_GLOBAL_H_

#include <cmath>
#include <iostream>
#include <list>
#include <map>
#include <string>
#include <vector>

/*
    New types
                */
typedef std::pair<int, int> int2;
typedef std::pair<double, double> double2;
/*  Define operations on type double2   */
extern double2 operator+(double2 const& a, double2 const& b);
extern double2 operator-(double2 const& a, double2 const& b);
extern double2 operator*(double2 const& a, double2 const& b);
extern double2 operator*(double const coef, double2 const& R);
extern double operator%(double2 const& a, double2 const& b);
extern double operator!(double2 const& a);
extern double2 operator^(double const a, double2 const& b);
/*  Define operations on type int2  */
extern int2 operator+(int2 const& a, int2 const& b);
extern int2 operator-(int2 const& a, int2 const& b);
extern int2 operator*(int2 const& a, int2 const& b);
/*
    Global variables
                        */
extern bool loadStaticData;

//  Geometry
extern std::vector<std::vector<double2>> listObstacles;
extern double Lx;
extern double Ly;

extern uint32_t nAgents;                           //  Number of agents
extern std::map<std::string, uint32_t> agentMap;   //  Correspondence between user-given ids and internal ids
extern std::vector<std::string> agentMapInverse;   //  Inverse version for output
struct Agent;                                      //  Defined in Agents.h
extern Agent** agents;                             //  The array of pointers to the agent objects

//  Time variables
extern double dt;        //  Time between two calls of the library
extern double dt_mech;   //  Time step of the mechanical layer

/*  Mechanical layer    */
extern std::vector<double2> agentProperties;   //  1 / tau_mech: translational and rotational damping
extern uint32_t nMaterials;
extern double** intrinsicProperties;
constexpr int nIntrinsicProperties = 2;
#if !defined(DOXYGEN_SHOULD_SKIP_THIS)
enum __attribute__((__packed__))
{
    YOUNG_MODULUS = 0,   //  E
    SHEAR_MODULUS = 1,   //  G
};
#endif   // DOXYGEN_SHOULD_SKIP_THIS
extern double*** binaryProperties;
constexpr int nBinaryProperties = 5;
#if !defined(DOXYGEN_SHOULD_SKIP_THIS)
enum __attribute__((__packed__))
{
    DAMPING_NORMAL = 0,         //  Gamma_n
    DAMPING_TANGENTIAL = 1,     //  Gamma_t
    STIFFNESS_NORMAL = 2,       //  k_n
    STIFFNESS_TANGENTIAL = 3,   //  k_t
    FRICTION_SLIDING = 4,       //  mu_dyn
};
#endif   // DOXYGEN_SHOULD_SKIP_THIS
extern std::vector<int32_t> obstaclesMaterial;
extern std::map<uint32_t, int32_t> shapesMaterial;

//  Paths
extern std::string pathStatic;
extern std::string pathDynamic;

/*
    Model parameters and user-defined constants
                                                */
//  Maximum speed of an agent
constexpr double vMaxAgent = 7.;

/*
    Function declarations
                            */
//  Utilities
std::pair<int, double2> parse2DComponents(const char* line);

//  Physics
inline double get_interval(const double x, const double length);
std::pair<double, double2> get_distance_to_wall_and_closest_point(double2 vertexA, double2 vertexB, const double2& C);
double get_distance(const double2& A, const double2& B);

#endif   // SRC_MECHANICAL_LAYER_INCLUDE_GLOBAL_H_
