"""Data loading utilities with caching and validation."""
import streamlit as st
import pandas as pd
from pathlib import Path

# Centralized file paths
DATA_DIR = Path(__file__).parent.parent / "data"
PROJECT_OCCUPATION_CSV = DATA_DIR / "project_occupation_data.csv"
PROJECT_OCCUPATION_SKILL_CSV = DATA_DIR / "project_occupation_skill_data.csv"
TRAINING_PROGRAM_BUNDLES_CSV = DATA_DIR / "training_program_bundles.csv"


@st.cache_data
def load_project_occupation_data() -> pd.DataFrame:
    """Load and validate project occupation data."""
    df = pd.read_csv(PROJECT_OCCUPATION_CSV)
    
    # Validate required columns
    required_cols = [
        'project_id', 'project_title', 'short_summary',
        'esco_id', 'occupation_esco', 'industry_cat_label',
        'onet_job_zone_label', 'pad_activities'
    ]
    missing = [col for col in required_cols if col not in df.columns]
    if missing:
        st.error(f"Missing required columns: {missing}")
        return pd.DataFrame()
    
    return df


@st.cache_data
def load_project_occupation_skill_data() -> pd.DataFrame:
    """Load and validate project occupation skill data."""
    df = pd.read_csv(PROJECT_OCCUPATION_SKILL_CSV)
    return df


@st.cache_data
def load_training_program_bundles() -> pd.DataFrame:
    """Load and validate training program bundles data."""
    df = pd.read_csv(TRAINING_PROGRAM_BUNDLES_CSV)
    return df
