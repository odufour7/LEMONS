How to test ```CrowdMechanics```
================================

After modifying the C++ code, you can run a series of eight tests (covering distinct scenarios) by following the steps below:

1. Navigate to the ``tests/mechanical_layer`` directory.
2. Run the following command in your terminal:

   .. code-block:: bash

      ./run_mechanical_tests

   The script will prompt you to enter the path to your ``ffmpeg`` application, which is required to generate movies from the simulation files.

.. note::

   If you do not already have ``ffmpeg`` installed, you can find installation instructions on the official website: `https://ffmpeg.org/ <https://ffmpeg.org/>`__

The results of the eight tests will appear in the movies directory. You will then have the possibility to look at all the videos and see if they meet your expectations.
The eight test scenarios are as follows:

1. **Agent pushing another agent** (``test_push_agent_agent`` folder)

   Tests the force orthogonal to the contact surface, representing a damped spring interaction between two agents.

2. **Agent colliding with a call** (``test_push_agent_wall`` folder)

   Tests the force orthogonal to the contact surface, representing a damped spring interaction between an agent and a wall.

3. **Agent sliding over other agents** (``test_slip_agent_agent`` folder)

   Tests the Coulomb friction interaction between two agents as one slides over the other.

4. **Agent sliding over a wall** (``test_slip_agent_wall`` folder)

   Tests the Coulomb friction interaction between an agent and a wall as the agent slides.

5. **Agent translating and relaxing** (``test_t_translation`` folder)

   Tests the behaviour as an agent undergoes a translation and gradually relaxes to a stationary state (no motion), due to the fluid-like force with the damping coefficient of :math:`1/t^{(\text{translation})}`.

6. **Agent rotating and relaxing** (``test_t_rotation`` folder)

   Tests the behaviour as an agent rotates and gradually relaxes to a stationary state (no motion), due to the fluid-like torque with the damping coefficient of :math:`1/t^{(\text{rotation})}`.

7. **Agent rolling over other agents without sliding** (``test_tangential_spring_agent_agent`` folder)

   Tests the force tangential to the contact surface, representing a damped spring interaction between two agents.

8. **Agent rolling over a wall without sliding** (``test_tangential_spring_agent_wall`` folder)

   Tests the force tangential to the contact surface, representing a damped spring interaction between an agent and a wall.
