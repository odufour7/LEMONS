"""Test script for running the mechanical layer engine in push agent wall scenario."""

import ctypes
import os
import xml.etree.ElementTree as ET
from pathlib import Path
from shutil import copyfile

# === Simulation Parameters ===
dt = 0.1  # Time step for the decisional layer (matches "TimeStep" in Parameters.xml)
Ndt = 30  # How many dt will be performed in total

# === Paths Setup ===
outputPath = Path("outputXML/")  # Directory to store output XML files
inputPath = Path("inputXML/")  # Directory to store input XML files
outputPath.mkdir(parents=True, exist_ok=True)  # Create directories if they don't exist
Path("dynamic/").mkdir(parents=True, exist_ok=True)
inputPath.mkdir(parents=True, exist_ok=True)
# Clean the input and output directory before starting
for file in list(inputPath.glob("*.xml")) + list(outputPath.glob("*.xml")) + list(Path("dynamic/").glob("*.xml")):
    os.remove(file)

# Copy the initial agent dynamics file to the dynamic folder
copyfile("../initial_agent_dynamics_files/AgentDynamics_test_push_agent_wall.xml", "dynamic/AgentDynamics.xml")

# === Loading the External Mechanics Library ===
# Adjust filename for OS (.so for Linux, .dylib for macOS)
Clibrary = ctypes.CDLL("../../../src/mechanical_layer/build/libCrowdMechanics.dylib")

agentDynamicsFilename = "AgentDynamics.xml"

# Prepare the list of XML files that will be passed to the DLL/shared library
files = [
    b"Parameters.xml",
    b"Materials.xml",
    b"Geometry.xml",
    b"Agents.xml",
    agentDynamicsFilename.encode("ascii"),  # Convert filename to bytes (required by ctypes)
]
nFiles = len(files)  # Number of configuration files to be passed
filesInput = (ctypes.c_char_p * nFiles)()  # Create a ctypes array of string pointers
filesInput[:] = files  # Populate array with the XML file names

# === Main Simulation Loop ===
for t in range(Ndt):
    print("Looping the Crowd mechanics engine - t=%.1fs..." % (t * dt))

    # 1. Save the current AgentDynamics file as input for this step (can be used for analysis later)
    copyfile("dynamic/" + agentDynamicsFilename, str(inputPath) + rf"/AgentDynamics input t={t * dt:.1f}.xml")

    # 2. Call the external mechanics engine, passing in the list of required XML files
    Clibrary.CrowdMechanics(filesInput)

    # 3. Save the updated AgentDynamics output to results folder (can be used for analysis later)
    copyfile("dynamic/" + agentDynamicsFilename, str(outputPath) + rf"/AgentDynamics output t={(t + 1) * dt:.1f}.xml")

    # 4. If the simulation produced an AgentInteractions.xml file, save that as well (optional output)
    try:
        copyfile("dynamic/AgentInteractions.xml", str(outputPath) + rf"/AgentInteractions t={(t + 1) * dt:.1f}.xml")
    except FileNotFoundError:
        # If the AgentInteractions file does not exist, skip copying
        pass

    # === Decision/Controller Layer for Next Step ===
    # Read the output AgentDynamics XML as input for the next run.
    # This is where you (or another program) can set new forces/moments for each agent for the next simulation step.
    XMLtree = ET.parse("dynamic/" + agentDynamicsFilename)
    agentsTree = XMLtree.getroot()

    # -- Assign random forces/moments to each agent --
    for agent in agentsTree.findall("Agent"):
        # Create new <Dynamics> tag for the agent (as the output file doesn't have it)
        dyn_elem = agent.find("Dynamics")
        # If the Dynamics element does not exist, create it
        if dyn_elem is None:
            dyn_elem = ET.SubElement(agent, "Dynamics")

        dyn_elem.set("Fp", "0.0,0.0")
        dyn_elem.set("Mp", "0.0")

    # Write the modified XML back, to be used in the next iteration
    XMLtree.write("dynamic/" + agentDynamicsFilename)
    # ================================================

# After all simulation steps are complete, print a final message.
print(f"Loop terminated at t={Ndt * dt:.1f}s!")
