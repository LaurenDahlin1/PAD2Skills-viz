"""Skills by Level Page - Which skills map to entry-level and advanced training pathways?"""
import streamlit as st
import pandas as pd
import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent))

from src.io import load_project_occupation_skill_data
from src.charts import create_heatmap
from src.styles import inject_custom_css
from src.chat import init_chat_session_state, handle_preset_question, render_chat_bottom_bar
from src.components import render_job_preparation_expander, render_floating_project_selector, render_project_info_button, render_previous_page_navigation

# Page config
st.set_page_config(
    page_title="Skills by Level - PAD2Skills",
    page_icon="🎓",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# Apply mobile-first CSS
inject_custom_css()

# Initialize chat session state
init_chat_session_state()

# Load data
df = load_project_occupation_skill_data()

if df.empty:
    st.error("Unable to load skill data. Please check data files.")
    st.stop()

# Validate required columns
required_cols = [
    'project_title', 'occupation_esco', 'onet_job_zone', 
    'onet_job_zone_label', 'skill_category_label', 'skill_label',
    'industry_cat_label', 'top_five'
]
missing = [col for col in required_cols if col not in df.columns]
if missing:
    st.error(f"Missing required columns: {missing}")
    st.stop()

# Map job zones to preparation categories
def map_preparation_category(job_zone):
    """Map O*NET job zone to preparation category."""
    if pd.isna(job_zone):
        return 'Unknown'
    zone = float(job_zone)
    if zone <= 2:
        return 'Low (1-2)'
    elif zone == 3:
        return 'Medium (3)'
    else:  # 4-5
        return 'High (4-5)'

# Helper function to shorten skill category names
def shorten_skill_category(name, max_length=19):
    """Shorten skill category name to max_length with ellipsis if needed.
    
    Reference: 'arts and humanities' = 19 chars
    """
    if pd.isna(name):
        return name
    name = str(name)
    if len(name) <= max_length:
        return name
    return name[:max_length-1] + "…"

df['preparation_category'] = df['onet_job_zone'].apply(map_preparation_category)

# Initialize session state for chatbot and filters
if 'selected_industry_skills' not in st.session_state:
    st.session_state.selected_industry_skills = None
if 'show_top_five_only' not in st.session_state:
    st.session_state.show_top_five_only = False

# Render floating project selector (using same session key as page 01)
selected_project = render_floating_project_selector(df, session_key="selected_project")

# Add spacing to prevent floating bar from blocking content
st.markdown("<div style='margin-top: 100px;'></div>", unsafe_allow_html=True)

# Main visual - Heatmap 
st.subheader("Which skills map to entry-level and advanced training pathways?")

# Show project info button if specific project selected
render_project_info_button(df, selected_project)

# Industry filter
col1, col2 = st.columns([1, 1])

with col1:
    st.markdown("**Select Industry**")
    # Filter out NaN values and convert to strings before sorting
    industries = df['industry_cat_label'].dropna().unique()
    industry_options = ["All Industries"] + sorted([str(x) for x in industries])
    selected_industry = st.selectbox(
        "Select Industry",
        options=industry_options,
        index=0,
        key="industry_selector_skills",
        label_visibility="collapsed"
    )

with col2:
    # Toggle for top 5 skills
    st.markdown("**Filter Options**")
    show_top_five = st.checkbox(
        "Use only top-5 skills per occupation",
        value=st.session_state.show_top_five_only,
        key="top_five_toggle"
    )

# Filter data based on selections
filtered_df = df.copy()

if selected_project != "ALL":
    filtered_df = filtered_df[filtered_df['project_title'] == selected_project]

if selected_industry != "All Industries":
    filtered_df = filtered_df[filtered_df['industry_cat_label'] == selected_industry]
    st.session_state.selected_industry_skills = selected_industry
else:
    st.session_state.selected_industry_skills = None

st.session_state.show_top_five_only = show_top_five

if show_top_five:
    filtered_df = filtered_df[filtered_df['top_five'] == True]

# Prepare data for heatmap
if not filtered_df.empty:
    # Set categorical order for preparation levels
    prep_order = ['Low (1-2)', 'Medium (3)', 'High (4-5)']
    filtered_df['preparation_category'] = pd.Categorical(
        filtered_df['preparation_category'], 
        categories=prep_order, 
        ordered=True
    )
    
    # Calculate counts
    heatmap_data = filtered_df.groupby(
        ['preparation_category', 'skill_category_label']
    ).size().reset_index(name='count')
    
    # Shorten skill category names for display
    heatmap_data['skill_category_display'] = heatmap_data['skill_category_label'].apply(shorten_skill_category)
    
    # Calculate percentages within each preparation category
    totals = heatmap_data.groupby('preparation_category')['count'].transform('sum')
    heatmap_data['percentage'] = (heatmap_data['count'] / totals * 100).round(1)
    
    fig = create_heatmap(
        df=heatmap_data,
        x_col='preparation_category',
        y_col='skill_category_display',
        value_col='percentage',
        title='',
        color_scale='Blues'
    )
    
    st.plotly_chart(
        fig,
        use_container_width=True,
        key="skills_heatmap"
    )
else:
    st.info("No skills found for the selected filters.")

st.markdown("---")

# Supporting content - Example Skills
if st.session_state.selected_industry_skills:
    st.subheader(f"Example Jobs: {st.session_state.selected_industry_skills}")
else:
    st.subheader("Example Skills")

# Show 3 random skills
if not filtered_df.empty:
    sample_skills = filtered_df.sample(n=min(3, len(filtered_df)), random_state=42)
    display_cols = {
        'occupation_esco': 'Occupation (ESCO)',
        'onet_job_zone_label': 'Preparation Level (O*NET)',
        'skill_category_label': 'Skill Category',
        'skill_label': 'Skill'
    }
    
    sample_display = sample_skills[list(display_cols.keys())].rename(columns=display_cols)
    st.dataframe(
        sample_display,
        use_container_width=True,
        hide_index=True,
        height=200
    )
else:
    st.info("No skills found for this selection.")

st.markdown("---")

# Details table in expander
with st.expander("📋 More Skill Details"):
    if not filtered_df.empty:
        # Make unique on occupation and skill to avoid duplicates when multiple projects share same occupation-skill
        details_df_unique = filtered_df.drop_duplicates(subset=['occupation_esco', 'skill_label'])
        
        # Sort and prepare display
        details_df_sorted = details_df_unique.sort_values([
            'preparation_category', 'skill_category_label', 'occupation_esco'
        ])
        
        # Table filters
        st.markdown("**Filter Table:**")
        col1, col2 = st.columns(2)
        
        with col1:
            prep_levels = ["All"] + sorted(details_df_sorted['onet_job_zone_label'].dropna().unique().tolist())
            selected_prep_filter = st.selectbox(
                "Preparation Level",
                options=prep_levels,
                index=0,
                key="table_prep_filter"
            )
        
        with col2:
            skill_categories = ["All"] + sorted(details_df_sorted['skill_category_label'].dropna().unique().tolist())
            selected_skill_cat_filter = st.selectbox(
                "Skill Category",
                options=skill_categories,
                index=0,
                key="table_skill_cat_filter"
            )
        
        # Apply table filters
        table_filtered = details_df_sorted.copy()
        if selected_prep_filter != "All":
            table_filtered = table_filtered[table_filtered['onet_job_zone_label'] == selected_prep_filter]
        if selected_skill_cat_filter != "All":
            table_filtered = table_filtered[table_filtered['skill_category_label'] == selected_skill_cat_filter]
        
        display_cols = {
            'occupation_esco': 'Occupation (ESCO)',
            'onet_job_zone_label': 'Preparation Level (O*NET)',
            'skill_category_label': 'Skill Category',
            'skill_label': 'Skill'
        }
        
        details_display = table_filtered[list(display_cols.keys())].rename(columns=display_cols)
        
        if not details_display.empty:
            # Pagination
            rows_per_page = 10
            total_rows = len(details_display)
            total_pages = (total_rows - 1) // rows_per_page + 1
            
            if 'skills_details_page' not in st.session_state:
                st.session_state.skills_details_page = 0
            
            # Reset page if out of bounds
            if st.session_state.skills_details_page >= total_pages:
                st.session_state.skills_details_page = 0
            
            # Page navigation
            col1, col2, col3 = st.columns([1, 2, 1])
            with col1:
                if st.button("⬅️ Previous", disabled=st.session_state.skills_details_page == 0, key="prev_skills"):
                    st.session_state.skills_details_page -= 1
                    st.rerun()
            with col2:
                st.write(f"Page {st.session_state.skills_details_page + 1} of {total_pages} ({total_rows} rows)")
            with col3:
                if st.button("Next ➡️", disabled=st.session_state.skills_details_page >= total_pages - 1, key="next_skills"):
                    st.session_state.skills_details_page += 1
                    st.rerun()
            
            # Display current page
            start_idx = st.session_state.skills_details_page * rows_per_page
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
                label=f"📥 Download Filtered Table ({total_rows} rows, CSV)",
                data=csv,
                file_name="skills_details_filtered.csv",
                mime="text/csv",
                use_container_width=True
            )
        else:
            st.info("No skills match the selected table filters. Try adjusting the filters above.")
    else:
        st.info("No skill details available. Try changing your filters.")

# About Job Preparation expander
render_job_preparation_expander()

st.markdown("---")

# Suggested question pills
st.markdown("### Ask PADdy (Chat)")
col1, col2 = st.columns(2)
with col1:
    if st.button("💡 What skills are suitable for entry-level training programs?", use_container_width=True, key="pill1_skills"):
        handle_preset_question("What skills are suitable for entry-level training programs?")
with col2:
    if st.button("💡 How do skills in this industry connect to the PAD objectives?", use_container_width=True, key="pill2_skills"):
        handle_preset_question("How do skills in this industry connect to the PAD objectives?")


# Navigation to previous page
render_previous_page_navigation()

# Add spacing to prevent floating bar from blocking content
st.markdown("<div style='margin-top: 50px;'></div>", unsafe_allow_html=True)

# Render floating chat bottom bar
def skills_chat_callback(user_message: str) -> str:
    """Generate response for skills page questions."""
    lower_msg = user_message.lower()
    if "entry" in lower_msg or "entry-level" in lower_msg:
        return "Entry-level roles (Job Zones 1-2) typically require basic communication, digital literacy, and fundamental technical skills."
    elif "industry" in lower_msg or "pad" in lower_msg or "objectives" in lower_msg:
        return "The skills shown above directly support the project activities and objectives outlined in the PADs."
    else:
        return f"Thanks for your question: '{user_message}'. I'm still learning!"

render_chat_bottom_bar(
    chat_placeholder="Ask PADdy about skills and training pathways.",
    on_message_callback=skills_chat_callback
)
