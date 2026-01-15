"""Data loading utilities with caching and validation."""
import streamlit as st
import pandas as pd
from pathlib import Path

# Google Drive direct download URLs
PROJECT_OCCUPATION_CSV_URL = "https://drive.google.com/uc?export=download&id=10a3OvZQs83fsP30Rz3xgNQ_MQqQlxiiz"
PROJECT_OCCUPATION_SKILL_CSV_URL = "https://drive.google.com/uc?export=download&id=1mKwe0CO9UJ4vEwcn9F5iEfISCR9gw6Lf"

# Legacy local paths (kept for reference)
DATA_DIR = Path(__file__).parent.parent / "data"
TRAINING_PROGRAM_BUNDLES_CSV = DATA_DIR / "training_program_bundles.csv"


def clean_industry_label(label: str) -> str:
    """Remove letter prefix from industry category labels.
    
    E.g., 'C Manufacturing' -> 'Manufacturing'
    """
    if pd.isna(label):
        return label
    label = str(label)
    # Remove "X " prefix (single letter + space)
    if len(label) > 2 and label[0].isalpha() and label[1] == ' ':
        return label[2:]
    return label


@st.cache_data
def load_project_occupation_data() -> pd.DataFrame:
    """Load and validate project occupation data from Google Drive."""
    df = pd.read_csv(PROJECT_OCCUPATION_CSV_URL)
    
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
    
    # Clean industry labels
    if 'industry_cat_label' in df.columns:
        df['industry_cat_label'] = df['industry_cat_label'].apply(clean_industry_label)
    
    return df


@st.cache_data
def load_project_occupation_skill_data() -> pd.DataFrame:
    """Load and validate project occupation skill data from Google Drive."""
    df = pd.read_csv(PROJECT_OCCUPATION_SKILL_CSV_URL)
    
    # Clean industry labels
    if 'industry_cat_label' in df.columns:
        df['industry_cat_label'] = df['industry_cat_label'].apply(clean_industry_label)
    
    return df


@st.cache_data
def load_training_program_bundles() -> pd.DataFrame:
    """Load and validate training program bundles data."""
    df = pd.read_csv(TRAINING_PROGRAM_BUNDLES_CSV)
    return df
