import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from utils import load_gapminder

df = load_gapminder()
df_latest = df[df['year'] == df['year'].max()]

st.header("What explains the differences?")
st.caption("BBD squiggle: drill from summary → individual country story")

if 'highlight_country' not in st.session_state:
    st.session_state.highlight_country = 'China'

countries = sorted(df_latest['country'].unique())
st.session_state.highlight_country = st.selectbox(
    "Highlight a country", countries,
    index=countries.index(st.session_state.highlight_country)
)
h = st.session_state.highlight_country
h_continent = df_latest[df_latest['country']==h]['continent'].values[0]

tab1, tab2 = st.tabs(["GDP vs Life Expectancy", "Continent comparison"])

with tab1:
    # BBD/SWD HIGHLIGHT colour
    colors = ['#E63946' if c == h else '#DDDDDD' for c in df_latest['country']]
    fig1 = go.Figure(go.Scatter(
        x=df_latest['gdpPercap'], y=df_latest['lifeExp'],
        mode='markers', marker=dict(color=colors, size=9, opacity=0.85),
        text=df_latest['country'], hovertemplate='%{text}<extra></extra>'
    ))
    fig1.add_annotation(
        x=df_latest[df_latest['country']==h]['gdpPercap'].values[0],
        y=df_latest[df_latest['country']==h]['lifeExp'].values[0],
        text=f'<b>{h}</b>', showarrow=True, arrowhead=1, ax=40, ay=-30,
        font=dict(color='#E63946', size=11, family='Arial')
    )
    fig1.update_xaxes(type='log', gridcolor='#EEEEEE', title='GDP per Capita (log)')
    fig1.update_yaxes(gridcolor='#EEEEEE', title='Life Expectancy (yrs)')
    fig1.update_layout(plot_bgcolor='white', paper_bgcolor='white', font=dict(family='Arial', size=12))
    st.plotly_chart(fig1, use_container_width=True)

with tab2:
    continent_df = df_latest[df_latest['continent']==h_continent].sort_values('lifeExp')
    # BBD HIGHLIGHT colour
    colors2 = ['#E63946' if c==h else '#2E75B6' for c in continent_df['country']]
    fig2 = go.Figure(go.Bar(
        x=continent_df['lifeExp'], y=continent_df['country'],
        orientation='h', marker_color=colors2, marker_line_width=0
    ))
    fig2.update_layout(
        title=f'{h} vs {h_continent} peers — life expectancy in {df_latest["year"].max()}',
        plot_bgcolor='white', paper_bgcolor='white', font=dict(family='Arial', size=12),
        xaxis=dict(gridcolor='#EEEEEE', range=[0, continent_df['lifeExp'].max()*1.1]),
        yaxis=dict(showgrid=False)
    )
    st.plotly_chart(fig2, use_container_width=True)
