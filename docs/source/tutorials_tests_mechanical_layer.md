## How to test ```CrowdMechanics```

This guide provides a structured overview of how to use the Kivy-based GUI to test our library.

The interface operates in three sequential stages controlled by <kbd>SPACE</kbd>:
  1. **Wall creation** (stage 1): Define the environment boundaries.
  2. **Agent placement** (stage 2): Add and configure agents within the environment.
  3. **Simulation** (stage 3): Run and observe agent dynamics.

You will find a comprehensive keybinding reference at the end to assist you, along with a guide to the graphical interface elements present on the canvas, including instructions on how to interpret them.


### Detailed workflow

After running the GUI from within the `tests/mechanical_layer` directory:
```bash
uv run python ScenarioGUI.py
```
proceed with the following detailed workflow.

#### 1. Wall creation (stage 1)
Begin by setting the simulation environment:
- **Left-click** to start or extend wall segments.
- **Right-click** to complete the current segment.
- Walls snap to grid nodes automatically.
- Press <kbd>SPACE</kbd> when your environment layout is complete.

#### 2. Agent placement (stage 2)
Next, add and configure agents:
- Press <kbd>a</kbd> to enter in agent placement mode.
- **Left-click** to place a new agent on the map.
- **Force mode** (<kbd>f</kbd>): *Right-click outside an agent, then drag and hold* to set propulsion force direction and magnitude (longer holds increase force).
- **Torque mode** (<kbd>t</kbd>):
  - *Left-click+hold outside the agent*: Apply positive torque.
  - *Right-click+hold outside the agent*: Apply negative torque.
- *Inside the agent*:
  - **Left-click+hold**: Rotate counter-clockwise.
  - **Right-click+hold**: Rotate clockwise.
- Press <kbd>SPACE</kbd> when your agents are all ready.


#### 3. Simulation (stage 3)
Finally, run and observe the simulation:
- Press <kbd>r</kbd> to run or start the mechanical layer simulation.
- Agents’ positions, velocities, and applied forces/torques update in real time.
- All force and torque settings persist across simulation steps.
- Once you have completed enough simulation steps, you can delete the dynamic folder, as well as the Agents.xml and Geometry.xml files.

### Keybindings reference

| Key | Functionality | Stage |
|-----|---------------|-------|
| <kbd>w</kbd> | Enter wall creation mode | All |
| <kbd>a</kbd> | Enter agent placement mode | All |
| <kbd>SPACE</kbd> | Advance to next stage | All |
| <kbd>f</kbd> | Force modification mode | Stage 2 |
| <kbd>t</kbd> | Torque modification mode | Stage 2 |
| <kbd>r</kbd> | Run simulation | Stage 3 |
| <kbd>s</kbd> | Save current configuration | All |
| <kbd>q</kbd> | Quit application | All |

### Graphical interface elements
- **Top and right panels** : Indicate the currently active mode.
- **Agent status panel**(bottom): Displays each agent’s position, orientation, velocities, and applied forces/torques.
- **Grid lines**: Spaced at 0.1m intervals for precise placement.
- **Propulsion force vectors**: Shown as arrows.
- **Active agent**: Displayed with full opacity for easy identification.
- **Saving**: Press s at any time to export your setup. The following files will be generated:
    - `Geometry.xml` — Wall layouts
    - `Agents.xml` — Agent properties
    - `AgentDynamics.xml` — Simulation states


