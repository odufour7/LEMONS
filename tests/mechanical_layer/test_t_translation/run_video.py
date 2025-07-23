"""Script for building the video of the crowd dynamics simulation in a simple translation scenario."""

import argparse
import os
import subprocess
from pathlib import Path

import matplotlib.pyplot as plt

import configuration.backup.dict_to_xml_and_reverse as fun_xml  # For converting XML to dictionary and vice versa
from configuration.models.crowd import create_agents_from_dynamic_static_geometry_parameters  # For creating agents based on XML data
from streamlit_app.plot import plot  # For plotting crowd data

# === Command Line Argument Parsing ===
parser = argparse.ArgumentParser(description="Export movie with configurable ffmpeg path.")
parser.add_argument("--ffmpeg", type=str, required=True, help="Path to the ffmpeg executable")
args = parser.parse_args()

# === Simulation Parameters ===
dt = 0.1  # Time step for the decisional layer (matches "TimeStep" in Parameters.xml)
Ndt = 30  # How many dt will be performed in total

# === Prepare the folders ===
# Define the paths to the folders you'll use
inputPath = Path("inputXML/")
staticPath = Path("./static")
plotsPath = Path("./plots")
plotsPath.mkdir(parents=True, exist_ok=True)  # Create plots directory if it doesn't exist

# Remove any old '.png' files in the plots directory
for file in plotsPath.glob("*.png"):
    os.remove(file)

# === Load static XML files ===
# Read the Agents.xml file as a string and convert it to a dictionary
with open(staticPath / "Agents.xml", encoding="utf-8") as f:
    crowd_xml = f.read()
static_dict = fun_xml.static_xml_to_dict(crowd_xml)

# Read the Geometry.xml file as a string and convert it to a dictionary
with open(staticPath / "Geometry.xml", encoding="utf-8") as f:
    geometry_xml = f.read()
geometry_dict = fun_xml.geometry_xml_to_dict(geometry_xml)

# === Loop over time steps ===
for t in range(Ndt):
    current_time = t * dt

    # Check if the dynamics file exists; if not, skip to the next time step
    dynamics_file = inputPath / f"AgentDynamics input t={current_time:.1f}.xml"
    if not dynamics_file.exists():
        print(f"Warning: {dynamics_file} not found, skipping.")
        continue

    # === Read and process the dynamics XML file ===
    # Read the current dynamics XML file as a string and convert it to a dictionary
    with open(dynamics_file, encoding="utf-8") as f:
        dynamic_xml = f.read()
    dynamic_dict = fun_xml.dynamic_xml_to_dict(dynamic_xml)

    # Create a crowd object using the configuration files data
    crowd = create_agents_from_dynamic_static_geometry_parameters(
        static_dict=static_dict,
        dynamic_dict=dynamic_dict,
        geometry_dict=geometry_dict,
    )

    # Plot and save the crowd as a PNG file
    plot.display_crowd2D(crowd)
    plt.savefig(plotsPath / rf"crowd2D_t={t:d}.png", dpi=300, format="png")
    plt.close()


# === Export to a movie with FFMPEG ===
ffmpeg = args.ffmpeg  # Get the ffmpeg path from command line arguments
movie_name = "test_t_translation"
plotsPath = Path("./plots")
moviesPath = Path("./movies")
moviesPath.mkdir(parents=True, exist_ok=True)
framerate = int(1.0 / dt)

for file in moviesPath.glob("*.mov"):
    os.remove(file)

# 1. Create an MP4 movie from PNG images in the plots folder
cmd1 = f"{ffmpeg} -framerate {framerate} -i {plotsPath}/crowd2D_t=%d.png {moviesPath}/{movie_name}.mp4"
subprocess.Popen(cmd1.split(), stdout=subprocess.PIPE).communicate()

# 2. Convert the MP4 to MOV for compatibility
cmd2 = f"{ffmpeg} -i {moviesPath}/{movie_name}.mp4 -pix_fmt yuv420p {moviesPath}/{movie_name}.mov"
subprocess.Popen(cmd2.split(), stdout=subprocess.PIPE).communicate()

# 3. Remove the intermediate MP4 file
cmd3 = f"rm {moviesPath}/{movie_name}.mp4"
subprocess.Popen(cmd3.split(), stdout=subprocess.PIPE).communicate()
