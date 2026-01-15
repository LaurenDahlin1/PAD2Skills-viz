"""Occupations Overview Page - What jobs are needed to accomplish PAD objectives?"""
import streamlit as st
import pandas as pd
import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent))

from src.io import load_project_occupation_data
from src.charts import create_donut_chart
from src.styles import inject_custom_css
from src.chat import init_chat_session_state, handle_preset_question, render_chat_bottom_bar
from src.components import render_job_preparation_expander, render_floating_project_selector, render_project_info_button, render_next_page_navigation

# Page config
st.set_page_config(
    page_title="Occupations Overview - PAD2Skills",
    page_icon="💼",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# Apply mobile-first CSS
inject_custom_css()

# Initialize chat session state
init_chat_session_state()

# Load data
df = load_project_occupation_data()

if df.empty:
    st.error("Unable to load data. Please check data files.")
    st.stop()

# Helper function to shorten industry names
def shorten_industry_name(name, max_length=29):
    """Shorten industry name to max_length with ellipsis if needed.
    
    Reference: 'S Arts Sports and Recreation' = 29 chars
    """
    if pd.isna(name):
        return name
    name = str(name)
    if len(name) <= max_length:
        return name
    return name[:max_length-1] + "…"

# Initialize session state for selected industry
if 'selected_industry' not in st.session_state:
    st.session_state.selected_industry = None

# Render floating project selector
selected_project = render_floating_project_selector(df, session_key="selected_project")

# Add spacing to prevent floating bar from blocking content
#st.markdown("<div style='margin-top: 25px;'></div>", unsafe_allow_html=True)
st.markdown("#")
#st.markdown("###")

# Main visual - Donut chart
st.subheader("What jobs are needed to deliver energy projects?")

# Show project info button if specific project selected
render_project_info_button(df, selected_project)

# Filter data based on project selection
if selected_project == "ALL":
    filtered_df = df.copy()
    # Make unique on esco_id by selecting random project
    filtered_df = filtered_df.groupby('esco_id').sample(n=1, random_state=42).reset_index(drop=True)
else:
    filtered_df = df[df['project_title'] == selected_project].copy()

# Prepare data for donut chart: count unique jobs by industry
industry_counts = filtered_df.groupby('industry_cat_label')['esco_id'].nunique().reset_index()
industry_counts.columns = ['Industry', 'Job Count']
industry_counts = industry_counts.sort_values('Job Count', ascending=False)

# Add rank and create display names with rank instead of letter prefix
industry_counts['Rank'] = range(1, len(industry_counts) + 1)

def format_industry_with_rank(row, max_length=29):
    """Format industry name with rank number and shorten if needed."""
    industry = row['Industry']
    rank = row['Rank']
    
    # Add rank number
    industry_with_rank = f"{rank} {industry}"
    
    # Shorten if needed
    if len(industry_with_rank) > max_length:
        return industry_with_rank[:max_length-1] + "…"
    return industry_with_rank

industry_counts['Industry_Display'] = industry_counts.apply(format_industry_with_rank, axis=1)

if not industry_counts.empty:
    fig = create_donut_chart(
        df=industry_counts,
        values_col='Job Count',
        names_col='Industry_Display',
        title="Occupation Counts by Industry",
        hole_size=0.4
    )
    
    st.plotly_chart(
        fig,
        use_container_width=True,
        key="industry_donut"
    )
    
    # Key indicators
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    
    with col1:
        total_occupations = filtered_df['esco_id'].nunique()
        st.markdown(f"<h2 style='text-align: center;'>{total_occupations}</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center;'>Occupations Found</p>", unsafe_allow_html=True)
    
    with col2:
        low_prep_count = filtered_df[filtered_df['onet_job_zone'].isin([1.0, 2.0])]['esco_id'].nunique()
        st.markdown(f"<h2 style='text-align: center;'>{low_prep_count}</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center;'>Low-Preparation Occupations</p>", unsafe_allow_html=True)
    
else:
    st.info("No occupations found for the selected project.")

st.markdown("---")

# Supporting content - Example jobs
if st.session_state.selected_industry:
    st.subheader(f"Example Jobs: {st.session_state.selected_industry}")
    example_df = filtered_df[filtered_df['industry_cat_label'] == st.session_state.selected_industry]
else:
    st.subheader("Example Jobs")
    example_df = filtered_df.copy()

# Industry filter inline in Example Jobs section
col1, col2 = st.columns([1, 3])
with col1:
    st.markdown("**Filter by Industry**")
with col2:
    # Create shortened display names for the dropdown
    industry_display_map = dict(zip(industry_counts['Industry'], industry_counts['Industry_Display']))
    industry_options = ["All Industries"] + [industry_display_map.get(ind, ind) for ind in industry_counts['Industry'].tolist()]
    industry_full_names = ["All Industries"] + industry_counts['Industry'].tolist()
    
    selected_industry_filter = st.selectbox(
        "Filter by Industry",
        options=industry_options,
        index=0,
        key="industry_filter",
        label_visibility="collapsed"
    )
    
    # Map back to full name for filtering
    if selected_industry_filter != "All Industries":
        selected_industry_idx = industry_options.index(selected_industry_filter)
        selected_industry_full = industry_full_names[selected_industry_idx]
        st.session_state.selected_industry = selected_industry_full
        example_df = filtered_df[filtered_df['industry_cat_label'] == selected_industry_full]
    else:
        st.session_state.selected_industry = None
        example_df = filtered_df.copy()

# Show 3 random jobs
if not example_df.empty:
    sample_jobs = example_df.sample(n=min(3, len(example_df)), random_state=42)
    display_cols = {
        'occupation_esco': 'Occupation (ESCO)',
        'onet_job_zone_label': 'Preparation Level (O*NET)',
        'pad_activities': 'Example PAD Activities'
    }
    
    sample_display = sample_jobs[list(display_cols.keys())].rename(columns=display_cols)
    st.dataframe(
        sample_display,
        use_container_width=True,
        hide_index=True,
        height=200
    )
else:
    st.info("No jobs found for this industry.")

st.markdown("---")

# Details table in expander
with st.expander("📋 More Job Details"):
    # Industry filter for details table
    col1, col2 = st.columns([1, 3])
    with col1:
        st.markdown("**Filter by Industry**")
    with col2:
        # Create shortened display names for the dropdown
        details_industry_display_map = dict(zip(industry_counts['Industry'], industry_counts['Industry_Display']))
        details_industry_options = ["All Industries"] + [details_industry_display_map.get(ind, ind) for ind in industry_counts['Industry'].tolist()]
        details_industry_full_names = ["All Industries"] + industry_counts['Industry'].tolist()
        
        selected_details_industry = st.selectbox(
            "Filter details by Industry",
            options=details_industry_options,
            index=0,
            key="details_industry_filter",
            label_visibility="collapsed"
        )
        
        # Map back to full name for filtering
        if selected_details_industry != "All Industries":
            selected_details_idx = details_industry_options.index(selected_details_industry)
            selected_details_full = details_industry_full_names[selected_details_idx]
            details_df = filtered_df[filtered_df['industry_cat_label'] == selected_details_full]
        else:
            details_df = filtered_df.copy()
    
    #st.markdown("##")
    
    if not details_df.empty:
        # Sort and prepare display
        details_df_sorted = details_df.sort_values(['industry_cat_label', 'occupation_esco'])
        
        # Shorten industry names in the details table
        details_df_sorted_display = details_df_sorted.copy()
        details_df_sorted_display['industry_cat_label'] = details_df_sorted_display['industry_cat_label'].apply(shorten_industry_name)
        
        display_cols = {
            'industry_cat_label': 'Industry',
            'occupation_esco': 'Occupation (ESCO)',
            'onet_job_zone_label': 'Preparation Level (O*NET)',
            'pad_activities': 'Example PAD Activities'
        }
        
        details_display = details_df_sorted_display[list(display_cols.keys())].rename(columns=display_cols)
        
        # Pagination
        rows_per_page = 10
        total_rows = len(details_display)
        total_pages = (total_rows - 1) // rows_per_page + 1
        
        if 'details_page' not in st.session_state:
            st.session_state.details_page = 0
        
        # Page navigation
        col1, col2, col3 = st.columns([1, 2, 1])
        with col1:
            if st.button("⬅️ Previous", disabled=st.session_state.details_page == 0):
                st.session_state.details_page -= 1
                st.rerun()
        with col2:
            st.write(f"Page {st.session_state.details_page + 1} of {total_pages}")
        with col3:
            if st.button("Next ➡️", disabled=st.session_state.details_page >= total_pages - 1):
                st.session_state.details_page += 1
                st.rerun()
        
        # Display current page
        start_idx = st.session_state.details_page * rows_per_page
        end_idx = min(start_idx + rows_per_page, total_rows)
        
        st.dataframe(
            details_display.iloc[start_idx:end_idx],
            use_container_width=True,
            hide_index=True,
            height=400
        )
        
        # Download button
        csv = details_display.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Full Table (CSV)",
            data=csv,
            file_name="occupations_details.csv",
            mime="text/csv",
            use_container_width=True
        )
    else:
        st.info("No job details available. Try changing your filters.")

# About Job Preparation expander
render_job_preparation_expander()

st.markdown("---")

# Suggested question pills
st.markdown("### Ask PADdy (Chat)")
col1, col2 = st.columns(2)
with col1:
    if st.button("💡 What industries have the most jobs?", use_container_width=True):
        handle_preset_question("What industries have the most jobs?")
with col2:
    if st.button("💡 What other data can I examine?", use_container_width=True):
        handle_preset_question("What other data can I examine?")

# Navigation to next page
render_next_page_navigation()

# Add spacing to prevent floating bar from blocking content
st.markdown("<div style='margin-top: 50px;'></div>", unsafe_allow_html=True)


# Render floating chat bottom bar
def occupation_chat_callback(user_message: str) -> str:
    """Generate response for occupation page questions."""
    lower_msg = user_message.lower()
    if "industries" in lower_msg and "most" in lower_msg:
        return "Based on the data, the top industries are shown in the chart above."
    elif "data" in lower_msg or "examine" in lower_msg:
        return "You can explore skills data and training programs in other pages."
    else:
        return f"Thanks for your question: '{user_message}'. I'm still learning!"

render_chat_bottom_bar(
    chat_placeholder="Ask PADdy about jobs and skills from Project Appraisal Documents.",
    on_message_callback=occupation_chat_callback
)

