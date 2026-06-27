import pandas as pd
import streamlit as st
import plotly.express as px

@st.cache_data
def load_gapminder():
    df = px.data.gapminder()
    return df
