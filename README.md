# PAD2Skills Visualization Dashboard

Mobile-first Streamlit dashboard for exploring occupations and skills data derived from World Bank Project Appraisal Documents (PADs).

## Overview

This dashboard provides an interactive interface to explore:
- **Occupations** needed to deliver energy projects
- **Skills** mapped to entry-level and advanced training pathways
- Connections between projects, industries, and workforce requirements

### To-Do

1. The dashboard pulls data from CSV files from Google Drive (see Data Source). Update the dashboard to make dynamic DB queries.
2. The chatbot is currently not active (though example responses are shown). Create embedding model, vector database, and chat endpoint. Connect to dashboard.

## Data Source

The data for this dashboard is generated from World Bank Project Appraisal Documents (PADs) using the [PAD2Skills](https://github.com/LaurenDahlin1/PAD2Skills) pipeline, which extracts occupations and skills from project documents.

### Visualization Data Files

- **[project_occupation_data_viz.csv](https://drive.google.com/file/d/1PwEvz3mAVBhbO5YYfIL4N2cqLo6qeIc6/view?usp=sharing)** - Subset of occupation data optimized for visualization
- **[project_occupation_skill_data_viz.csv](https://drive.google.com/file/d/1ZjPBBrUxDTrbtsVZON1HTJhUhd9-r1cy/view?usp=drive_link)** - Subset of occupation-skill mappings optimized for visualization

### Full Data Files

These files contain the complete dataset with additional columns not used in the visualization. These additional columns will be included in the chatbot.

- **[project_occupation_data.csv](https://drive.google.com/file/d/1E75FbEXs7kKKQ3tGaf_TdKATZ91JX76C/view?usp=sharing)** - Full occupation data with all columns
- **[project_occupation_skill_data.csv](https://drive.google.com/file/d/1BWf_MiyleiHPIVPq-p7qLxbaUcryJWfZ/view?usp=sharing)** - Full occupation-skill mappings (large file!)

## Setup

This project uses [uv](https://github.com/astral-sh/uv) for fast, reliable Python dependency management.

### Prerequisites
- Python 3.11+
- uv (install via `curl -LsSf https://astral.sh/uv/install.sh | sh`)

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd PAD2Skills-viz

# Install dependencies with uv
uv sync

# Run the dashboard
uv run streamlit run streamlit_app.py
```

## Project Structure

```
PAD2Skills-viz/
├── streamlit_app.py          # Main entry point (redirects to first page)
├── pages/
│   ├── 01_Occupations_Overview.py  # Occupations by industry
│   └── 02_Skills_by_Level.py       # Skills by preparation level
├── src/
│   ├── io.py                 # Data loading utilities
│   └── charts.py             # Plotly chart generators
├── data/
│   ├── project_occupation_data.csv
│   ├── project_occupation_skill_data.csv
│   └── training_program_bundles.csv
└── pyproject.toml            # Project dependencies
```

## Features

### Page 1: Occupations Overview
- Donut chart showing occupations by industry
- Project filtering
- Example jobs table with preparation levels
- Paginated details table with download option

### Page 2: Skills by Level
- Heatmap showing skill distribution across preparation levels (Low/Medium/High)
- Percentage-based visualization
- Industry and project filters
- Top-5 skills toggle
- Filterable details table with preparation level and skill category filters

### Mobile-First Design
- Responsive layout optimized for phone screens
- Collapsed sidebar with hamburger menu navigation
- Touch-friendly controls and spacing
- Full-width charts and tables

## Technology Stack

- **Frontend**: Streamlit
- **Charts**: Plotly
- **Data**: pandas
- **Package Management**: uv
- **Python**: 3.11+

## Development

```bash
# Run a specific page directly
uv run streamlit run pages/01_Occupations_Overview.py

# Clear cache and restart
find . -type d -name __pycache__ -exec rm -rf {} + && uv run streamlit run PAD2Skills.py
```

## License

This project is licensed under the Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License. See [LICENSE](LICENSE) for details.
