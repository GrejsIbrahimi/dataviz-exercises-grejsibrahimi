#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jun 18 18:50:24 2026

@author: dina.deifallah
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path


# @st.cache_data: Streamlit reruns the entire script on every widget interaction.
# Without caching, the CSV is read from disk on every interaction — slow and wasteful.
# cache_data stores the result after the first run and reuses it until the file changes

@st.cache_data
def load_data():
    # Përshtatur që të gjejë datasetin direkt në folderin week10 si ushtrimi i parë
    path = Path(__file__).parent / 'co2_emissions.csv'
    if not path.exists():
        path = Path(__file__).parent.parent / 'data' / 'co2_emissions.csv'
    df = pd.read_csv(path)
    df['Date'] = pd.to_datetime(df['Year'].astype(str) + '-01-01')
    return df

df = load_data()

st.title("CO₂ Emissions Explorer")

with st.sidebar:
    st.header("Filters")
    
    # filter 1: Multi-select country
    selected_countries = st.multiselect(
        "Countries", sorted(df['Country'].unique()),
        default=['China', 'United States', 'India', 'Germany']
    )
    
    # guard against empty country selection
    if not selected_countries:
        st.warning("Select at least one country.")
        st.stop()
        
    # filter 2: slider for year range - use when year is cast as an integer
    # Tuple default → two-handle range slider
    year_range = st.slider("Year range",
        int(df['Year'].min()), int(df['Year'].max()), (2010, 2020))
    
    # ── FIXING TOO MANY COLORS: Added highlight selector ─────────────────────
    st.markdown("---")
    st.subheader("Highlight Settings")
    country_to_highlight = st.selectbox(
        "Select Country to Highlight", 
        options=selected_countries
    )
    
# applying filtering by country and year range 
filtered = df[
    df['Country'].isin(selected_countries) &
    (df['Year'] >= year_range[0]) &
    (df['Year'] <= year_range[1])
]

# for clarity: showing the number of countries and the number of data points selected
st.caption(f"Showing {len(selected_countries)} countries | {len(filtered)} data points")


# Figure 1: Line chart (Fixed the 'too many colors' issue via Grey-and-Highlight)

# Ndërtojmë një fjalor ngjyrash: shteti i zgjedhur merr ngjyrë të kuqe, të tjerët gri
color_map = {}
for country in selected_countries:
    if country == country_to_highlight:
        color_map[country] = '#FF4B4B'  # E kuqe e fortë për fokus
    else:
        color_map[country] = '#D3D3D3'  # Gri e zbehtë për të tjerët

# Ekzekutojmë grafikun duke përdorur fjalorin tonë të ngjyrave (color_discrete_map)
fig = px.line(filtered, x='Year', y='CO2_Mt', color='Country',
              labels={'CO2_Mt': 'CO2 (Mt)'},
              color_discrete_map=color_map)

fig.update_layout(
    plot_bgcolor='white', 
    paper_bgcolor='white',
    font=dict(family='Arial'),
    # Shtojmë titull inteligjent siç i pëlqen zyshës
    title=f"<b>Emissions Trend: {country_to_highlight} Highlighted</b>"
)

# Pastrojmë rrjetën e grafikut për pamje më të pastër (Clean Layout)
fig.update_xaxes(showgrid=True, gridcolor='#f2f2f2')
fig.update_yaxes(showgrid=True, gridcolor='#f2f2f2')

st.plotly_chart(fig, use_container_width=True)