import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

st.set_page_config(page_title="CO2 Dashboard", page_icon="🌱", layout="wide")

# ── Data Loading (Fixed Path and Columns) ─────────────────────────────────────
@st.cache_data
def load_data():
    # Looks directly inside the week10 folder for the dataset
    path = Path(__file__).parent / 'co2_emissions.csv'
    df = pd.read_csv(path)
    
    # Clean column names from any hidden spaces and make matching foolproof
    df.columns = df.columns.str.strip()
    
    # Map column names if they are slightly different
    rename_dict = {}
    for col in df.columns:
        if 'co2' in col.lower() and 'capita' in col.lower():
            rename_dict[col] = 'CO2 per capita'
        elif 'co2' in col.lower() and ('total' in col.lower() or 'mt' in col.lower()):
            rename_dict[col] = 'Total CO2 (Mt)'
            
    df = df.rename(columns=rename_dict)
    
    # If Total CO2 (Mt) is missing but we have per capita and population, calculate it
    if 'Total CO2 (Mt)' not in df.columns and 'CO2 per capita' in df.columns and 'Population' in df.columns:
        df['Total CO2 (Mt)'] = (df['CO2 per capita'] * df['Population']) / 1_000_000
    elif 'Total CO2 (Mt)' not in df.columns:
        # Fallback if names are completely custom
        for col in df.columns:
            if 'co2' in col.lower():
                df['Total CO2 (Mt)'] = df[col]
                break
                
    df['Date'] = pd.to_datetime(df['Year'].astype(str) + '-01-01')
    return df

df = load_data()

st.title("🌱 CO2 Emissions Explorer")
st.caption("Source: Our World in Data — ourworldindata.org/co2-emissions")


# ── TASK 1: Sidebar with 5 widgets ────────────────────────────────────────────
st.sidebar.header("Dashboard Filters")

# a) st.selectbox for Region (with 'All')
regions = ["All"] + sorted(df['Region'].unique().tolist())
selected_region = st.sidebar.selectbox("Select Region", regions)

# Filter dataset by region first to chain the country selection dynamically
if selected_region != "All":
    df_region = df[df['Region'] == selected_region]
else:
    df_region = df

# b) st.multiselect for Countries (Chained)
available_countries = sorted(df_region['Country'].unique().tolist())
selected_countries = st.sidebar.multiselect("Select Countries", available_countries, default=available_countries[:4])

# Guard rails: stop app execution if no country is selected
if not selected_countries:
    st.warning("Please select at least one country to view the charts.")
    st.stop()

# Filter data down to selected countries
df_filtered = df_region[df_region['Country'].isin(selected_countries)]

# c) st.date_input for date range
min_year = int(df_filtered['Year'].min())
max_year = int(df_filtered['Year'].max())

selected_years = st.sidebar.slider("Select Year Range", min_value=min_year, max_value=max_year, value=(min_year, max_year))

# Filter data down to the selected year range
df_filtered = df_filtered[(df_filtered['Year'] >= selected_years[0]) & (df_filtered['Year'] <= selected_years[1])]

# d) st.radio for Metric selection
metric_options = []
if 'Total CO2 (Mt)' in df_filtered.columns:
    metric_options.append('Total CO2 (Mt)')
if 'CO2 per capita' in df_filtered.columns:
    metric_options.append('CO2 per capita')
if not metric_options:
    metric_options = [df_filtered.columns[2]] # Backup if everything fails

metric_choice = st.sidebar.radio("Select Metric", metric_options)

# e) st.checkbox for highlighting top emitter
highlight_top = st.sidebar.checkbox("Show only top emitter highlighted")


# ── TASK 2: Filter summary caption ────────────────────────────────────────────
total_countries_count = len(selected_countries)
summary_text = f"📊 {total_countries_count} countries selected | Region: {selected_region} | Range: {selected_years[0]}-{selected_years[1]} | Metric: {metric_choice}"
st.info(summary_text)


# ── EXTENSION: KPI row above the charts ───────────────────────────────────────
kpi_container = st.container()
with kpi_container:
    kpi_col1, kpi_col2, kpi_col3 = st.columns(3)
    
    last_year = selected_years[1]
    df_last_year = df_filtered[df_filtered['Year'] == last_year]
    
    if not df_last_year.empty:
        # Use whatever column name is current
        target_col = 'Total CO2 (Mt)' if 'Total CO2 (Mt)' in df_last_year.columns else metric_choice
        total_emissions_sum = df_last_year[target_col].sum()
        highest_emitter_row = df_last_year.loc[df_last_year[metric_choice].idxmax()]
        
        kpi_col1.metric(f"Total Emissions ({last_year})", f"{total_emissions_sum:,.1f} Mt")
        kpi_col2.metric(f"Top Emitter ({last_year})", highest_emitter_row['Country'])
        kpi_col3.metric(f"Highest Value ({last_year})", f"{highest_emitter_row[metric_choice]:,.2f}")


# ── TASK 3: Two charts reacting to ALL filters ────────────────────────────────
col_left, col_right = st.columns([2, 1])

with col_left:
    st.subheader("Emission Trends Over Time")
    
    if highlight_top and not df_filtered.empty:
        top_country = df_filtered.loc[df_filtered[metric_choice].idxmax()]['Country']
        color_map = {c: "#FF4B4B" if c == top_country else "#D3D3D3" for c in df_filtered['Country'].unique()}
        
        fig_line = px.line(
            df_filtered, x="Year", y=metric_choice, color="Country",
            color_discrete_map=color_map,
            title=f"<b>{top_country} Leads Regional Carbon Footprint Growth Within Selection Range</b><br><span style='font-size:13px; color:#666666'>Grey-and-highlight analysis targeting the maximum emitter country.</span>"
        )
    else:
        fig_line = px.line(
            df_filtered, x="Year", y=metric_choice, color="Country",
            color_discrete_sequence=px.colors.qualitative.Safe,
            title="<b>Yearly CO2 Generation Slopes Tracking Across Selected Nations</b><br><span style='font-size:13px; color:#666666'>Continuous tracking across the complete chosen time window.</span>"
        )
        
    fig_line.update_layout(
        plot_bgcolor="white", 
        xaxis=dict(showgrid=True, gridcolor="#f2f2f2"), 
        yaxis=dict(showgrid=True, gridcolor="#f2f2f2")
    )
    st.plotly_chart(fig_line, use_container_width=True)

with col_right:
    st.subheader("Current Year Standings")
    
    if not df_last_year.empty:
        fig_bar = px.bar(
            df_last_year.sort_values(by=metric_choice, ascending=True),
            x=metric_choice,
            y="Country",
            orientation="h",
            color=metric_choice,
            color_continuous_scale="Plasma",
            title=f"<b>Emissions Standings Ranking in {last_year}</b><br><span style='font-size:13px; color:#666666'>Horizontal ranking based on selected metrics.</span>"
        )
        fig_bar.update_layout(
            plot_bgcolor="white", 
            xaxis=dict(showgrid=True, gridcolor="#f2f2f2")
        )
        st.plotly_chart(fig_bar, use_container_width=True)
    else:
        st.info("No data available for the bar chart ranking.")