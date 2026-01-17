"""Plotly chart generators for mobile-first visualizations."""
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd


def create_donut_chart(
    df: pd.DataFrame,
    values_col: str,
    names_col: str,
    title: str,
    hole_size: float = 0.4
) -> go.Figure:
    """
    Create a mobile-friendly donut chart.
    
    Args:
        df: DataFrame with aggregated data
        values_col: Column name for values
        names_col: Column name for labels
        title: Chart title
        hole_size: Size of center hole (0-1)
    
    Returns:
        Plotly Figure
    """
    # Use a clean color palette
    colors = px.colors.qualitative.Prism
    
    fig = go.Figure(data=[go.Pie(
        labels=df[names_col],
        values=df[values_col],
        hole=hole_size,
        hovertemplate="<b>%{label}</b><br>Occupations: %{value}<br>Percentage: %{percent}<extra></extra>",
        textposition='none',  # Remove text from slices
        textinfo='none',  # No text on slices
        marker=dict(colors=colors, line=dict(color='white', width=2)),
        pull=[0.05 if i < 3 else 0 for i in range(len(df))],  # Pull out top 3 slices slightly
    )])
    
    fig.update_layout(
        title_text='',
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.15,
            xanchor="center",
            x=0.5,
            font=dict(size=10),
            bgcolor="rgba(255,255,255,0.8)",
            bordercolor="rgba(0,0,0,0.1)",
            borderwidth=1
        ),
        margin=dict(l=10, r=10, t=60, b=150),  # More bottom margin for legend
        height=700,
        autosize=True,
        paper_bgcolor='white',
        plot_bgcolor='white',
        annotations=[dict(
            text='<b>Occupation Counts<br>by Industry</b>',
            x=0.18,
            y=0.5,
            font_size=15,
            font_color='#2a2a2a',
            font_family="-apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif",
            showarrow=False,
            xref="paper",
            yref="paper",
            align="left",
            bgcolor='rgba(240, 240, 240, 0.6)',  # Light gray transparent background
            borderpad=8
        )] if title else []    )
    
    return fig


def create_horizontal_bar_chart(
    df: pd.DataFrame,
    x_col: str,
    y_col: str,
    title: str,
    color_col: str = None
) -> go.Figure:
    """
    Create a mobile-friendly horizontal bar chart with wrapped y-axis labels.
    
    Args:
        df: DataFrame with data
        x_col: Column for x-axis (values)
        y_col: Column for y-axis (categories)
        title: Chart title
        color_col: Optional column for color coding
    
    Returns:
        Plotly Figure
    """
    # Wrap y-axis labels every three words
    def wrap_label(text: str, words_per_line: int = 3, max_words: int = 6) -> str:
        """Insert <br> tag every N words in the label, truncate after max_words."""
        words = str(text).split()
        
        # Truncate if too long
        if len(words) > max_words:
            words = words[:max_words]
            words[-1] = words[-1] + '…'
        
        wrapped_lines = []
        for i in range(0, len(words), words_per_line):
            wrapped_lines.append(' '.join(words[i:i+words_per_line]))
        return '<br>'.join(wrapped_lines)
    
    # Create a copy and wrap labels
    df_plot = df.copy()
    df_plot[y_col + '_wrapped'] = df_plot[y_col].apply(wrap_label)
    
    # Create horizontal bar chart with custom blue color
    fig = go.Figure(data=[go.Bar(
        x=df_plot[x_col],
        y=df_plot[y_col + '_wrapped'],
        orientation='h',
        marker=dict(color='#08273f'),
        text=df_plot[x_col],
        textposition='outside',
        hovertemplate="<b>%{y}</b><br>Occupations: %{x}<extra></extra>"
    )])
    
    fig.update_layout(
        title=dict(text=title, x=0.5, xanchor='center', font=dict(size=16)),
        xaxis_title=None,
        yaxis_title=None,
        showlegend=False,
        margin=dict(l=20, r=20, t=50, b=20),
        height=max(300, len(df) * 50),  # More height per bar for wrapped labels
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
    )
    
    # Remove grid lines
    fig.update_xaxes(showgrid=False, zeroline=False)
    fig.update_yaxes(showgrid=False, zeroline=False)
    
    fig.update_traces(textposition='outside')
    
    return fig


def create_heatmap(
    df: pd.DataFrame,
    x_col: str,
    y_col: str,
    value_col: str,
    title: str,
    color_scale: str = "Blues"
) -> go.Figure:
    """
    Create a mobile-friendly heatmap.
    
    Args:
        df: DataFrame with data
        x_col: Column for x-axis (categories)
        y_col: Column for y-axis (categories)
        value_col: Column for values (heat intensity)
        title: Chart title
        color_scale: Plotly color scale name
    
    Returns:
        Plotly Figure
    """
    # Pivot data for heatmap
    pivot_data = df.pivot_table(
        index=y_col,
        columns=x_col,
        values=value_col,
        aggfunc='sum',
        fill_value=0
    )
    
    # Detect if values are percentages (likely if max value is <= 100)
    is_percentage = pivot_data.values.max() <= 100
    
    fig = go.Figure(data=go.Heatmap(
        z=pivot_data.values,
        x=pivot_data.columns,
        y=pivot_data.index,
        colorscale=color_scale,
        hovertemplate='%{y}<br>%{x}<br>' + ('Percentage: %{z}%' if is_percentage else 'Count: %{z}') + '<extra></extra>',
        colorbar=dict(
            title=dict(
                text="Concentration of Skills (%)" if is_percentage else "Count",
                side='top'
            ),
            thickness=12,
            len=0.6,
            orientation='h',
            x=0.5,
            xanchor='center',
            y=-0.12,
            yanchor='top',
            tickfont=dict(size=10)
        )
    ))
    
    fig.update_layout(
        title=dict(
            text=title,
            x=0.5,
            xanchor='center',
            font=dict(size=16, color='#2a2a2a')
        ),
        xaxis=dict(
            title=dict(
                text="Job Preparation Level",
                font=dict(size=12, color='#2a2a2a')
            ),
            side='top',
            tickfont=dict(size=11),
            tickangle=0
        ),
        yaxis=dict(
            title=None,
            tickfont=dict(size=11),
            autorange='reversed'
        ),
        margin=dict(l=150, r=20, t=60, b=100),
        height=max(400, len(pivot_data) * 40),
        paper_bgcolor='white',
        plot_bgcolor='white',
    )
    
    return fig
