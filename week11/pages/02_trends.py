import streamlit as st
import plotly.express as px
from utils import load_gapminder

df = load_gapminder()
st.header("How has life expectancy changed?")

with st.sidebar:
    st.header("Filters")
    continents = st.multiselect("Continent", df['continent'].unique(), default=list(df['continent'].unique()))
    metric = st.radio("Metric", ["Life Expectancy", "GDP per Capita"])

if not continents:
    st.warning("Select at least one continent.")
    st.stop()

y_col = 'lifeExp' if metric == "Life Expectancy" else 'gdpPercap'
avg = df[df['continent'].isin(continents)].groupby(['continent','year'])[y_col].mean().reset_index()

# BBD CATEGORICAL colour
fig = px.line(avg, x='year', y=y_col, color='continent',
              labels={y_col: metric, 'year': ''},
              title=f'Global {metric.lower()} has risen steadily — Asia shows the steepest gains')
fig.update_layout(plot_bgcolor='white', paper_bgcolor='white', font=dict(family='Arial', size=12),
                  yaxis=dict(gridcolor='#EEEEEE'), xaxis=dict(showgrid=False),
                  legend=dict(orientation='h', y=1.08))
st.plotly_chart(fig, use_container_width=True)
