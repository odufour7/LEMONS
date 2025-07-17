"""User interface module."""

# Copyright  2025  Institute of Light and Matter, CNRS UMR 5306
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

from pathlib import Path
from typing import Any

import streamlit as st
from streamlit_option_menu import option_menu

import streamlit_app.utils.constants as cst_app


def setup_app() -> None:
    """Set up the Streamlit page configuration."""
    st.set_page_config(
        page_title=f"{cst_app.PROJECT_NAME} Project",
        page_icon=":bar_chart:",
        layout="wide",
        initial_sidebar_state="expanded",
        menu_items={
            "Get Help": "https://github.com/odufour7/LEMONS",
            "Report a bug": "https://github.com/odufour7/LEMONS/issues",
            "About": f"# {cst_app.PROJECT_NAME} Project " + ":flag-fr:",
        },
    )


def menubar() -> Any:
    """
    Create a menu bar with multiple tabs and icons.

    Returns
    -------
    Any
        The selected option from the menu bar.

    Notes
    -----
    - Streamlit's `st.markdown` is used to apply custom CSS styles.
    - The `option_menu` function creates the menu bar with specified tabs and icons.
    - The `unsafe_allow_html=True` parameter enables Streamlit to render raw HTML and CSS.
    - The `styles` dictionary customizes the appearance of the menu bar.
    - The icon can be changed using resources from https://icons.getbootstrap.com/.
    """
    # Custom CSS rules to handle multi-line text alignment and indentation, that applies to the entire app.
    st.markdown(
        """
        <style>
        .nav-link {
            display: flex;
            align-items: center;
            white-space: pre-wrap; /* Ensures that long text wraps onto multiple lines without breaking formatting */
            text-align: left;
        }
        .nav-link div {
            margin-left: 10px; /* Adjust margin to align text with icon */
        }
        .nav-link div span {
            display: block;
            padding-left: 20px; /* Simulate tab space */
        }
        </style>
        """,
        unsafe_allow_html=True,  # enables Streamlit to render raw HTML and CSS
    )
    return option_menu(
        f"{cst_app.PROJECT_NAME} project",
        [
            cst_app.FIRST_TAB_NAME,
            cst_app.SECOND_TAB_NAME,
            cst_app.THIRD_TAB_NAME,
            cst_app.FOURTH_TAB_NAME,
        ],
        icons=[
            "person-fill",
            "people-fill",
            "bar-chart-line",
            "info-square",
        ],
        menu_icon="cast",
        default_index=0,
        orientation="horizontal",
        styles={
            "container": {
                "padding": "0!important",  # Removes padding from container. (generate space around an element's content)
                "background-color": "#fafafa",  # Sets the background color of the container to a light gray shade (#fafafa).
            },
            "icon": {"color": "red", "font-size": "15px"},
            "nav-link": {
                "font-size": "15px",
                "text-align": "left",
                "margin": "0px",
                "--hover-color": "#fafafa",  # Sets the hover color to a light gray shade (#eee).
            },
        },
    )


def init_sidebar_looks() -> None:
    """
    Initialize the appearance of the sidebar.

    - Displays a GitHub repository badge with a link to the repository.
    - Displays a DOI badge with a link to the DOI.
    - Displays a logo image from the assets directory.
    """
    current_file_path = Path(__file__)
    ROOT_DIR = current_file_path.parent.parent.parent.parent.absolute()
    logo_path = ROOT_DIR / "docs" / "source" / "_static" / "logo" / "logo_app.png"
    article_badge = "[![](https://badgen.net/badge/DOI/open%20access/orange)](https://scipost.org/SciPostPhysCodeb)"
    doc_badge = "[![](https://badgen.net/static/DOC/lemons-docs/cyan?icon=https://icons.getbootstrap.com/icons/filetype-doc/)](https://shapes-crowd.readthedocs.io/en/latest/index.html)"
    gh = "https://badgen.net/badge/icon/GitHub?icon=github&label"
    repo = "https://github.com/odufour7/LEMONS"
    repo_badge = f"[![]({gh})]({repo})"

    c1, c2 = st.sidebar.columns((0.25, 0.8))
    c1.write("**Article**")
    c2.write(article_badge)
    c1.write("**Doc**")
    c2.write(doc_badge)
    c1.write("**Repo**")
    c2.markdown(repo_badge, unsafe_allow_html=True)

    st.sidebar.image(str(logo_path), use_container_width=True)

    st.sidebar.warning("⚠️ All measurements in this app are displayed in centimeters.")
