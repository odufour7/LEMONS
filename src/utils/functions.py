"""This module contains utility functions for data processing and manipulation."""

import json
import pickle
from pathlib import Path
from typing import Any
from xml.dom.minidom import parseString

import numpy as np
import pandas as pd
import streamlit as st
from dicttoxml import dicttoxml
from scipy.stats import truncnorm
from shapely.geometry import MultiPolygon
from streamlit.delta_generator import DeltaGenerator

import src.utils.constants as cst
from src.classes.measures import CrowdMeasures
from src.utils.typing_custom import AgentPart, BackupDataType, SapeDataType


def load_pickle(file_path: Path) -> Any:
    """Loads a pickle file from the specified path."""
    with open(file_path, "rb") as f:
        data = pickle.load(f)
    return data


def save_pickle(data, file_path: Path) -> None:
    """Saves data to a pickle file at the specified path."""
    with open(file_path, "wb") as f:
        pickle.dump(data, f)


@st.cache_data
def load_data(filename):
    """Load a CSV file as a pandas DataFrame."""
    return pd.read_csv(filename)


def wrap_angle(angle: float) -> float:
    """Wrap an angle to the range [-180, 180)."""
    return (angle + 180.0) % (2 * 180.0) - 180.0


def get_shapes_data(backup_data_type: BackupDataType, shapes_data: SapeDataType) -> tuple[str, str]:
    """Prepare the shapes data based on the specified format."""
    if backup_data_type == cst.BackupDataTypes.json.name:
        # Convert the dictionary to JSON
        data = json.dumps(shapes_data, indent=4)
        mime_type = "application/json"
    elif backup_data_type == cst.BackupDataTypes.xml.name:
        # Convert the dictionary to XML
        xml_data = dicttoxml(shapes_data, custom_root="shapes", attr_type=False)
        # Parse the XML string
        dom = parseString(xml_data)
        # Pretty-print the XML with indentation
        pretty_xml = dom.toprettyxml(indent="  ")
        # Remove empty lines
        data = "\n".join([line for line in pretty_xml.split("\n") if line.strip()])
        mime_type = "application/xml"
    elif backup_data_type == cst.BackupDataTypes.pickle.name:
        # Convert the dictionary to a pickle byte stream
        data = pickle.dumps(shapes_data)
        mime_type = "application/octet-stream"
    else:
        raise ValueError(f"Unsupported backup data type: {backup_data_type}")

    return data, mime_type


def extract_coordinates(multi_polygon: MultiPolygon) -> tuple[np.ndarray, np.ndarray]:
    """Extracts the x and y coordinates of a MultiPolygon."""
    all_x, all_y = [], []
    for polygon in multi_polygon.geoms:
        x, y = polygon.exterior.xy
        all_x.extend(x)
        all_y.extend(y)
    return np.array(all_x), np.array(all_y)


def filter_mesh_by_z_threshold(
    all_points: np.ndarray, all_triangles: np.ndarray, z_threshold: float = 0.3
) -> tuple[np.ndarray, np.ndarray]:
    """Filters a 3D mesh by removing vertices and triangles associated with z-coordinates below a given threshold."""
    # Step 1: Identify valid vertices (z > threshold)
    valid_vertices_mask = all_points[:, 2] > z_threshold
    valid_indices = np.where(valid_vertices_mask)[0]

    # Step 2: Create a mapping from old vertex indices to new ones
    old_to_new_index = np.full(all_points.shape[0], -1)  # Initialize with -1 for invalid indices
    old_to_new_index[valid_indices] = np.arange(len(valid_indices))  # Map valid indices to new positions

    # Step 3: Filter triangles where all three vertices are valid
    valid_triangles_mask = np.all(np.isin(all_triangles, valid_indices), axis=1)
    filtered_triangles = all_triangles[valid_triangles_mask]

    # Step 4: Update triangle indices to reflect the new vertex indexing
    filtered_triangles = old_to_new_index[filtered_triangles]

    # Step 5: Filter the vertices based on the valid mask
    filtered_points = all_points[valid_vertices_mask]

    return filtered_points, filtered_triangles


def update_progress_bar(progress_bar: DeltaGenerator, status_text: DeltaGenerator, frac: float) -> None:
    """Update the progress bar and status text."""
    # Update progress bar
    percent_complete = int(frac * 100)
    progress_bar.progress(percent_complete)
    # Update status text
    progress_text = "Operation in progress. Please wait. ⏳"
    status_text.text(f"{progress_text} {percent_complete}%")


def draw_from_trunc_normal(mean: float, std_dev: float, min_val: float, max_val: float) -> float:
    """Draw a random value from a truncated normal distribution."""
    a = (min_val - mean) / std_dev
    b = (max_val - mean) / std_dev
    return truncnorm.rvs(a, b, loc=mean, scale=std_dev)


def draw_sex(p):
    """Draw male with probability p or female with probability 1-p"""
    if not 0 <= p <= 1:
        raise ValueError("Probability p must be between 0 and 1.")
    return "male" if np.random.random() < p else "female"


# TODO : rename in draw from statistics maybe rather than from database
def draw_agent_part(agent_part: AgentPart, crowd_statistics: CrowdMeasures) -> float:
    """Draw a random value for the specified agent part from a truncated normal distribution."""
    if agent_part == cst.PedestrianParts.chest_depth.name:
        mean = crowd_statistics.pedestrian_statistics[cst.CrowdPedestrianStat.mean_chest_depth.name]
        std_dev = crowd_statistics.pedestrian_statistics[cst.CrowdPedestrianStat.std_dev_chest_depth.name]
        min_val = crowd_statistics.pedestrian_statistics[cst.CrowdPedestrianStat.min_chest_depth.name]
        max_val = crowd_statistics.pedestrian_statistics[cst.CrowdPedestrianStat.max_chest_depth.name]
        return draw_from_trunc_normal(mean, std_dev, min_val, max_val)
    if agent_part == cst.PedestrianParts.bideltoid_breadth.name:
        mean = crowd_statistics.pedestrian_statistics[cst.CrowdPedestrianStat.mean_bideltoid_breadth.name]
        std_dev = crowd_statistics.pedestrian_statistics[cst.CrowdPedestrianStat.std_dev_bideltoid_breadth.name]
        min_val = crowd_statistics.pedestrian_statistics[cst.CrowdPedestrianStat.min_bideltoid_breadth.name]
        max_val = crowd_statistics.pedestrian_statistics[cst.CrowdPedestrianStat.max_bideltoid_breadth.name]
        return draw_from_trunc_normal(mean, std_dev, min_val, max_val)
    if agent_part == cst.PedestrianParts.sex.name:
        return draw_sex(crowd_statistics.pedestrian_statistics[cst.CrowdPedestrianStat.male_proportion.name])
    if agent_part == cst.BikeParts.handlebar_length.name:
        mean = crowd_statistics.bike_statistics[cst.CrowdBikeStat.mean_handlebar_length.name]
        std_dev = crowd_statistics.bike_statistics[cst.CrowdBikeStat.std_dev_handlebar_length.name]
        min_val = crowd_statistics.bike_statistics[cst.CrowdBikeStat.min_handlebar_length.name]
        max_val = crowd_statistics.bike_statistics[cst.CrowdBikeStat.max_handlebar_length.name]
        return draw_from_trunc_normal(mean, std_dev, min_val, max_val)
    if agent_part == cst.BikeParts.top_tube_length.name:
        mean = crowd_statistics.bike_statistics[cst.CrowdBikeStat.mean_top_tube_length.name]
        std_dev = crowd_statistics.bike_statistics[cst.CrowdBikeStat.std_dev_top_tube_length.name]
        min_val = crowd_statistics.bike_statistics[cst.CrowdBikeStat.min_top_tube_length.name]
        max_val = crowd_statistics.bike_statistics[cst.CrowdBikeStat.max_top_tube_length.name]
        return draw_from_trunc_normal(mean, std_dev, min_val, max_val)
    if agent_part == cst.BikeParts.total_length.name:
        mean = crowd_statistics.bike_statistics[cst.CrowdBikeStat.mean_total_length.name]
        std_dev = crowd_statistics.bike_statistics[cst.CrowdBikeStat.std_dev_total_length.name]
        min_val = crowd_statistics.bike_statistics[cst.CrowdBikeStat.min_total_length.name]
        max_val = crowd_statistics.bike_statistics[cst.CrowdBikeStat.max_total_length.name]
        return draw_from_trunc_normal(mean, std_dev, min_val, max_val)
    if agent_part == cst.BikeParts.wheel_width.name:
        mean = crowd_statistics.bike_statistics[cst.CrowdBikeStat.mean_wheel_width.name]
        std_dev = crowd_statistics.bike_statistics[cst.CrowdBikeStat.std_dev_wheel_width.name]
        min_val = crowd_statistics.bike_statistics[cst.CrowdBikeStat.min_wheel_width.name]
        max_val = crowd_statistics.bike_statistics[cst.CrowdBikeStat.max_wheel_width.name]
        return draw_from_trunc_normal(mean, std_dev, min_val, max_val)
    raise ValueError(f"Unknown agent part: {agent_part}")
