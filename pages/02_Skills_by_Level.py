"""Skills by Level Page - Which skills map to entry-level and advanced training pathways?"""
import streamlit as st
import pandas as pd
import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent))

from src.io import load_project_occupation_skill_data
from src.charts import create_heatmap

# Page config
st.set_page_config(
    page_title="Skills by Level - PAD2Skills",
    page_icon="🎓",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# Mobile CSS (same as 01_occupations_overview.py)
MOBILE_CSS = """
<style>
/* Professional font stack */
* {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Helvetica Neue', Arial, sans-serif;
}

/* Safe zone for mobile notches and status bars */
.block-container { 
    padding-top: max(3rem, env(safe-area-inset-top)); 
    padding-bottom: 3rem;
    padding-left: env(safe-area-inset-left);
    padding-right: env(safe-area-inset-right);
}

h1 { 
    font-size: 1.6rem; 
    margin-top: 1rem; 
    font-weight: 600;
    letter-spacing: -0.02em;
    color: #1a1a1a;
}

h2 { 
    font-size: 1.25rem; 
    font-weight: 600;
    letter-spacing: -0.01em;
    color: #2a2a2a;
}

h3 { 
    font-size: 1.05rem; 
    font-weight: 600;
    color: #3a3a3a;
}

/* Better body text */
p, div, span {
    color: #4a4a4a;
    line-height: 1.6;
}

div[data-testid="stVerticalBlock"] > div { width: 100%; }

/* Chatbot output box styling */
.chatbot-box {
    background-color: #f0f2f6;
    border: 1px solid #e0e0e0;
    border-radius: 8px;
    padding: 1rem;
    margin-bottom: 1.5rem;
    font-size: 0.95rem;
    line-height: 1.6;
    color: #2a2a2a;
}

.chatbot-emoji {
    font-size: 1.5em;
    vertical-align: middle;
    margin-right: 0.5rem;
}

/* Reduce spacing around selectors */
div[data-testid="stSelectbox"] {
    margin-bottom: 0.5rem;
}

/* Reduce top padding on plotly charts */
div[data-testid="stPlotlyChart"] {
    margin-top: -0.5rem;
}

/* Better button styling */
button {
    font-weight: 500;
    letter-spacing: 0.01em;
}

/* Better caption styling */
.caption {
    font-size: 0.875rem;
    color: #6a6a6a;
    font-weight: 400;
}

/* Prevent auto-scroll to chat input on load */
div[data-testid="stChatInput"] {
    scroll-margin-top: 0;
}

@media (max-width: 640px) {
  .block-container { 
    padding-left: max(0.75rem, env(safe-area-inset-left)); 
    padding-right: max(0.75rem, env(safe-area-inset-right)); 
  }
  h1 { font-size: 1.35rem; }
  .chatbot-box { font-size: 0.9rem; }
}
</style>
"""
st.markdown(MOBILE_CSS, unsafe_allow_html=True)

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
if 'skills_chatbot_output' not in st.session_state:
    st.session_state.skills_chatbot_output = "Hi, I'm PADdy."
if 'selected_industry_skills' not in st.session_state:
    st.session_state.selected_industry_skills = None
if 'show_top_five_only' not in st.session_state:
    st.session_state.show_top_five_only = False

# Chatbot output at top in styled box
st.markdown(
    f'<div class="chatbot-box"><span class="chatbot-emoji">🤖</span>{st.session_state.skills_chatbot_output}</div>',
    unsafe_allow_html=True
)

# Main visual - Heatmap
st.subheader("Which skills map to entry-level and advanced training pathways?")

# Global filters
col1, col2 = st.columns(2)

with col1:
    st.markdown("**Select Project**")
    project_options = ["ALL"] + sorted(df['project_title'].unique().tolist())
    selected_project = st.selectbox(
        "Select Project",
        options=project_options,
        index=0,
        key="project_selector_skills",
        label_visibility="collapsed"
    )

with col2:
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

# Filter data based on selections
filtered_df = df.copy()

if selected_project != "ALL":
    filtered_df = filtered_df[filtered_df['project_title'] == selected_project]

if selected_industry != "All Industries":
    filtered_df = filtered_df[filtered_df['industry_cat_label'] == selected_industry]
    st.session_state.selected_industry_skills = selected_industry
else:
    st.session_state.selected_industry_skills = None

# Toggle for top 5 skills
st.markdown("**Filter Options**")
show_top_five = st.checkbox(
    "Show only top-5 skills per occupation",
    value=st.session_state.show_top_five_only,
    key="top_five_toggle"
)
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
with st.expander("📋 More Skill Details+"):
    if not filtered_df.empty:
        # Sort and prepare display
        details_df_sorted = filtered_df.sort_values([
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
    if st.button("💡 What skills are suitable for entry-level training programs?", use_container_width=True, key="pill1_skills"):
        st.session_state.skills_chatbot_output = "🤖 Entry-level roles (Job Zones 1-2) typically require basic communication, digital literacy, and fundamental technical skills."
        st.rerun()
with col2:
    if st.button("💡 How do skills in this industry connect to the PAD objectives?", use_container_width=True, key="pill2_skills"):
        st.session_state.skills_chatbot_output = "🤖 The skills shown above directly support the project activities and objectives outlined in the PADs."
        st.rerun()

chat_input = st.chat_input("Ask PADdy about skills and training pathways.", key="skills_chat")
if chat_input:
    st.session_state.skills_chatbot_output = f"🤖 Thanks for your question: '{chat_input}'. I'm still learning!"
    st.rerun()
