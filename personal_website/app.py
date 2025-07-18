import streamlit as st
import pandas as pd

st.title("Personal Website")
st.write("Welcome to my personal website!")
st.sidebar.title("Navigation")
st.sidebar.write("Use the sidebar to navigate through different sections.")
st.sidebar.markdown("[Home](#home)")
st.sidebar.markdown("[About Me](#about-me)")
st.sidebar.markdown("[Projects](#projects)")
st.sidebar.markdown("[Contact](#contact)")
