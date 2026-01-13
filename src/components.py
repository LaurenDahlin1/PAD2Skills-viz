"""Reusable UI components for the PAD2Skills dashboard."""

import streamlit as st
import pandas as pd
from streamlit_float import float_init
from st_keyup import st_keyup


def render_floating_project_selector(df: pd.DataFrame, session_key: str = "selected_project") -> str:
    """Render a floating project selector bar at the top of the page.
    
    Args:
        df: DataFrame containing project_title column
        session_key: Session state key for storing selected project (default: "selected_project")
        
    Returns:
        Selected project name or "ALL"
    """
    # Initialize session state
    if session_key not in st.session_state:
        st.session_state[session_key] = "ALL"
    if f'{session_key}_search' not in st.session_state:
        st.session_state[f'{session_key}_search'] = ""
    
    # Get project options
    project_options = ["ALL"] + sorted(df['project_title'].unique().tolist())
    
    # Helper function to select a project
    def select_project(project_name: str):
        """Update selected project in session state."""
        st.session_state[session_key] = project_name
        st.session_state[f'{session_key}_search'] = ""  # Clear search after selection
    
    # Initialize float
    float_init()
    
    # Dynamic expander label based on selection
    if st.session_state[session_key] == "ALL":
        num_projects = len(project_options) - 1  # Exclude "ALL"
        expander_label = f"Select a Project (Showing {num_projects} Projects)"
    else:
        # Truncate long project names for the label
        proj_name = st.session_state[session_key]
        expander_label = proj_name if len(proj_name) <= 65 else proj_name[:62] + "..."
    
    top_project_bar = st.container()
    with top_project_bar:
        with st.expander(expander_label, expanded=False):
            # Search box for filtering projects
            search_query = st_keyup(
                "Search projects",
                key=f"{session_key}_search_input",
                placeholder="Search projects...",
                label_visibility="collapsed"
            )
            
            # Filter projects based on search
            if search_query:
                filtered_projects = [p for p in project_options if search_query.lower() in p.lower()]
            else:
                filtered_projects = project_options
            
            # Show "ALL" button first if it matches search
            if "ALL" in filtered_projects:
                is_selected = st.session_state[session_key] == "ALL"
                btn_type = "primary" if is_selected else "secondary"
                if st.button(
                    "Show All Projects" + (" ✓" if is_selected else ""),
                    key=f"btn_all_{session_key}",
                    use_container_width=True,
                    type=btn_type
                ):
                    select_project("ALL")
                    st.rerun()
            
            # Show project buttons (excluding ALL)
            project_list = [p for p in filtered_projects if p != "ALL"]
            
            if not project_list and search_query:
                st.caption("No projects match your search.")
            else:
                # Show projects in a scrollable container
                scroll_container = st.container(height=300)
                with scroll_container:
                    for project in project_list:
                        is_selected = st.session_state[session_key] == project
                        btn_type = "primary" if is_selected else "secondary"
                        display_name = project
                        if st.button(
                            display_name + (" ✓" if is_selected else ""),
                            key=f"btn_{session_key}_{project}",
                            use_container_width=True,
                            type=btn_type
                        ):
                            select_project(project)
                            st.rerun()
    
    # Float the bar at the top
    top_project_bar.float(
        "position: fixed; top: 0;"
        "z-index: 998; background: white; "
        "padding: 0.75rem 1rem; "
        "padding-top: 75px; "
        "border-bottom: 1px solid rgba(49,51,63,0.2); "
        "background-color: #08273f;"
    )
    
    return st.session_state[session_key]


def render_project_info_button(df: pd.DataFrame, selected_project: str):
    """Render project info button and dialog when a specific project is selected.
    
    Args:
        df: DataFrame containing project_title and short_summary columns
        selected_project: Name of the selected project or "ALL"
    """
    if selected_project != "ALL":
        project_summary = df[df['project_title'] == selected_project]['short_summary'].iloc[0]
        
        @st.dialog("Project Details")
        def show_project_info():
            st.write(f"**{selected_project}**")
            st.write(project_summary)
        
        if st.button("ℹ️ Project Info", use_container_width=True):
            show_project_info()


def render_job_preparation_expander():
    """Render the 'About Job Preparation' expander with O*NET job zone descriptions."""
    with st.expander("📚 About Job Preparation"):
        st.markdown("""
The job preparation levels are mapped from O*NET's job zones, shown below.

**Low Preparation**

- **Job Zone One: Little or No Preparation Needed**: Little or no previous work-related skill, knowledge, or experience is needed for these occupations. For example, a person can become a waiter or waitress even if he/she has never worked before. Some of these occupations may require a secondary education. Employees in these occupations need anywhere from a few days to a few months of training. Usually, an experienced worker could show you how to do the job.

- **Job Zone Two: Some Preparation Needed**: Some previous work-related skill, knowledge, or experience is usually needed. For example, a teller would benefit from experience working directly with the public. These occupations usually require secondary education. Employees in these occupations need anywhere from a few months to one year of working with experienced employees. A recognized apprenticeship program may be associated with these occupations.

**Medium Preparation**

- **Job Zone Three: Medium Preparation Needed**: Previous work-related skill, knowledge, or experience is required for these occupations. For example, an electrician must have completed three or four years of apprenticeship or several years of vocational training, and often must have passed a licensing exam, in order to perform the job. Most occupations in this zone require training in vocational schools, related on-the-job experience, or an associate's degree. Employees in these occupations usually need one or two years of training involving both on-the-job experience and informal training with experienced workers. A recognized apprenticeship program may be associated with these occupations.

**High Preparation**

- **Job Zone Four: Considerable Preparation Needed**: A considerable amount of work-related skill, knowledge, or experience is needed for these occupations. For example, an accountant must complete four years of college and work for several years in accounting to be considered qualified. Most of these occupations require a post-secondary degree, but some do not. Employees in these occupations usually need several years of work-related experience, on-the-job training, and/or vocational training.

- **Job Zone Five: Extensive Preparation Needed**: Extensive skill, knowledge, and experience are needed for these occupations. Many require more than five years of experience. For example, surgeons must complete four years of college and an additional five to seven years of specialized medical training to be able to do their job. Most of these occupations require graduate school. For example, they may require a master's degree, and some require a Ph.D., M.D., or J.D. (law degree). Employees may need some on-the-job training, but most of these occupations assume that the person will already have the required skills, knowledge, work-related experience, and/or training.
    """)


def render_next_page_navigation(
    page_title: str = "Explore Skills by Job Level",
    page_icon: str = "🎓",
    page_number: str = "02",
    description: str = "See which skills are needed for entry-level vs. advanced positions"
) -> None:
    """Render a navigation card to guide users to the next page.
    
    Args:
        page_title: Title of the next page
        page_icon: Emoji icon for the page
        page_number: Page number/identifier (e.g., "02")
        description: Brief description of what users will find
    """
    st.markdown("---")
    
    # Create a visually appealing navigation card
    col1, col2 = st.columns([5, 1])
    
    with col1:
        st.markdown(f"### {page_icon} {page_title}")
        st.caption(description)
    
    with col2:
        # Next arrow button that navigates to next page
        if st.button("Next →", key="next_arrow_nav_button", use_container_width=True, type="secondary"):
            st.switch_page(f"pages/{page_number}_Skills_by_Level.py")


def render_previous_page_navigation(
    page_title: str = "Back to Occupations",
    page_icon: str = "💼",
    page_number: str = "01",
    description: str = "Return to the occupations overview"
) -> None:
    """Render a navigation card to guide users to the previous page.
    
    Args:
        page_title: Title of the previous page
        page_icon: Emoji icon for the page
        page_number: Page number/identifier (e.g., "01")
        description: Brief description of what users will find
    """
    st.markdown("---")
    
    # Create a visually appealing navigation card
    col1, col2 = st.columns([1, 5])
    
    with col1:
        # Back arrow button that navigates to previous page
        if st.button("← Back", key="back_arrow_nav_button", use_container_width=True, type="secondary"):
            st.switch_page(f"pages/{page_number}_Occupations_Overview.py")
    
    with col2:
        st.markdown(f"### {page_icon} {page_title}")
        st.caption(description)
