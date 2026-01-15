"""Data loading utilities with caching and validation."""
import streamlit as st
import pandas as pd
from pathlib import Path
import io
import requests

# Google Drive file IDs
PROJECT_OCCUPATION_FILE_ID = "1PwEvz3mAVBhbO5YYfIL4N2cqLo6qeIc6"
PROJECT_OCCUPATION_SKILL_FILE_ID = "1ZjPBBrUxDTrbtsVZON1HTJhUhd9-r1cy"

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


def download_google_drive_file(file_id: str) -> pd.DataFrame:
    """Download a CSV from Google Drive, handling large file confirmations.
    
    Google Drive requires a confirmation token for files that trigger virus scan warnings.
    """
    # Try direct download first
    url = f"https://drive.google.com/uc?export=download&id={file_id}"
    
    try:
        # First attempt - works for small files
        df = pd.read_csv(url)
        return df
    except Exception as e:
        # If that fails, try with requests to handle confirmation
        try:
            session = requests.Session()
            response = session.get(url, stream=True)
            
            # Check if we need to confirm (large file)
            if 'confirm' in response.text or 'virus' in response.text.lower():
                # Extract confirmation token
                for key, value in response.cookies.items():
                    if key.startswith('download_warning'):
                        url = f"https://drive.google.com/uc?export=download&id={file_id}&confirm={value}"
                        break
                response = session.get(url)
            
            # Read the CSV content
            df = pd.read_csv(io.StringIO(response.text))
            return df
        except Exception as e2:
            st.error(f"Failed to load file {file_id}: {str(e2)}")
            st.error("Please verify the file is shared publicly (Anyone with the link can view)")
            return pd.DataFrame()


@st.cache_data
def load_project_occupation_data() -> pd.DataFrame:
    """Load and validate project occupation data from Google Drive."""
    df = download_google_drive_file(PROJECT_OCCUPATION_FILE_ID)
    
    if df.empty:
        return df
    
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
    df = download_google_drive_file(PROJECT_OCCUPATION_SKILL_FILE_ID)
    
    if df.empty:
        return df
    
    # Clean industry labels
    if 'industry_cat_label' in df.columns:
        df['industry_cat_label'] = df['industry_cat_label'].apply(clean_industry_label)
    
    return df


@st.cache_data
def load_training_program_bundles() -> pd.DataFrame:
    """Load and validate training program bundles data."""
    df = pd.read_csv(TRAINING_PROGRAM_BUNDLES_CSV)
    return df
