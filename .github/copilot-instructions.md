# Copilot Instructions — Streamlit Mobile-First Dashboard

## Purpose
You are helping build a **mobile-first Streamlit dashboard** that lets users explore **World Bank PAD projects**, the **occupations** referenced in each project, and the **skills** linked to those occupations. The app is intended to support workforce-planning discussions (e.g., what training programs could be created for the jobs implied by projects).

The repo includes CSV files as the source of truth. Code should be organized, reusable, and easy to iterate on.

## Tech stack requirements
- **Python + Streamlit** for the UI.
- **Plotly** for *all* charts (no Altair, no Matplotlib).
- **pandas** for data loading and manipulation.
- Use `uv` for environment/dependency management (assume dependencies already declared in `pyproject.toml`).

## Mobile-first UI requirements (critical)
Design for a phone screen first, then scale up.
- Prefer `st.set_page_config(layout="centered", initial_sidebar_state="collapsed")`.
- Keep the top of each page concise: title + 1 sentence description + key filters.
- Avoid dense layouts and wide tables. Use:
  - Short summaries / KPI tiles
  - Tabs
  - Expanders for secondary content
- Make every chart and control **full-width** on mobile.
- Use readable typography and spacing:
  - Limit long paragraphs
  - Use `st.caption()` / short helper text instead of long blocks
- Keep interactions simple:
  - 1–2 primary filters per page
  - Avoid requiring the sidebar for core navigation

### Responsive CSS pattern
If CSS is needed, inject it once in the Streamlit entrypoint (e.g., `app.py`) and keep it minimal. Use media queries for small screens.

## Visual theme requirements
- White/light theme.
- Clean, minimal, high-contrast UI.
- Avoid heavy borders/shadows. Use whitespace instead.
- Use a single accent color for highlights (links, selected states) if needed.

## Plotly chart rules (critical)
All charts must be Plotly and must render well on mobile.
- Use `st.plotly_chart(fig, use_container_width=True)`.
- Prefer:
  - Horizontal bars over vertical when labels are long
  - Treemap/sunburst only if it stays readable on mobile
  - Donut charts only for small category counts; otherwise bar chart
- Ensure:
  - Short titles
  - Legible axis labels (rotate or shorten as needed)
  - Tooltips enabled and useful
- Keep color usage simple and consistent across charts.

## Data handling and performance
- Load CSVs with `st.cache_data`.
- Keep data transformations in small, testable functions in `src/`.
- Avoid recomputing expensive aggregations on every rerun; cache derived tables when helpful.
- Be robust to missing columns / empty data and show a user-friendly message.

### Standard patterns
- `src/io.py`: cached CSV loaders and validation (required columns, dtypes).
- `src/transforms.py`: groupbys, joins, derived fields.
- `src/charts.py`: functions that return Plotly figures.

## Navigation and page patterns
Use Streamlit multipage (`pages/`) or a clear internal navigation scheme. Each page should follow:
1. Chat bot output at top with robot emoji 🤖. If no output, it should say "Hi, I'm PADdy."
2. Main chart title
3. Filters
4. Primary chart
5. Details table in an expander
6. Chat bot input with pills just above it to suggest questions.

## Tables (mobile-friendly)
- Prefer summary tables with a small number of columns.
- Use `st.dataframe(..., use_container_width=True, hide_index=True)`.
- When tables are wide, provide:
  - Column selection
  - Download button
  - Scroll
- Paginate tables

## Specific features to include (recommended)
Implement these features unless clearly out of scope for the current task.

### 1) Global filter bar (top of page)
A consistent filter experience:
- Project selector (All vs single project)
- Optional: Sector/industry selector

### 2) Downloads
Provide downloads for:
- Filtered occupations table (CSV)
- Filtered skills table (CSV)
Use `st.download_button`.

## Coding style
- Prefer small pure functions with clear names.
- Type hints where helpful.
- Do not hardcode file paths; centralize them in `src/io.py`.
- Handle errors gracefully (no stack traces shown to users in normal flow).
- Keep pages thin: pages assemble UI; `src/` contains logic.

## What to do when requirements conflict
Prioritize in this order:
1. Mobile usability
2. Plotly-only charts
3. Clear, simple UI and navigation
4. Code organization and reuse
5. Performance optimizations