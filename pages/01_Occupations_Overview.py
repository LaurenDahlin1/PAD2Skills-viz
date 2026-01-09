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

# Page config
st.set_page_config(
    page_title="Occupations Overview - PAD2Skills",
    page_icon="💼",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# Apply mobile-first CSS
inject_custom_css()

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

# Initialize session state for chatbot and industry selection
if 'chatbot_output' not in st.session_state:
    st.session_state.chatbot_output = "Hi, I'm PADdy."
if 'selected_industry' not in st.session_state:
    st.session_state.selected_industry = None

# Chatbot output at top in styled box
st.markdown(f'<div class="chatbot-box"><span class="chatbot-emoji">🤖</span>{st.session_state.chatbot_output}</div>', unsafe_allow_html=True)

# Main visual - Donut chart
st.subheader("What jobs are needed to deliver energy projects?")

# Project filter under the heading
col1, col2 = st.columns([1, 3])
with col1:
    st.markdown("**Select Project**")
with col2:
    project_options = ["ALL"] + sorted(df['project_title'].unique().tolist())
    selected_project = st.selectbox(
        "Select Project",
        options=project_options,
        index=0,
        key="project_selector",
        label_visibility="collapsed"
    )

# Show project info button if specific project selected
if selected_project != "ALL":
    project_summary = df[df['project_title'] == selected_project]['short_summary'].iloc[0]
    
    @st.dialog("Project Details")
    def show_project_info():
        st.write(f"**{selected_project}**")
        st.write(project_summary)
    
    if st.button("ℹ️ Project Info", use_container_width=True):
        show_project_info()

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

# Shorten industry names for display
industry_counts['Industry_Display'] = industry_counts['Industry'].apply(shorten_industry_name)

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
with st.expander("📋 More Job Details+"):
    if st.session_state.selected_industry:
        details_df = filtered_df[filtered_df['industry_cat_label'] == st.session_state.selected_industry]
    else:
        details_df = filtered_df.copy()
    
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
with st.expander("📚 About Job Preparation+"):
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

st.markdown("---")

# Chat input + pills at bottom
st.caption("Ask PADdy")

# Pills for suggested questions
col1, col2 = st.columns(2)
with col1:
    if st.button("💡 What industries have the most jobs?", use_container_width=True):
        st.session_state.chatbot_output = "🤖 Based on the data, the top industries are shown in the chart above."
        st.rerun()
with col2:
    if st.button("💡 What other data can I examine?", use_container_width=True):
        st.session_state.chatbot_output = "🤖 You can explore skills data and training programs in other pages."
        st.rerun()

chat_input = st.chat_input("Ask PADdy about jobs and skills from Project Appraisal Documents.")
if chat_input:
    st.session_state.chatbot_output = f"🤖 Thanks for your question: '{chat_input}'. I'm still learning!"
    st.rerun()