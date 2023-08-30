"""
# My FPL app
Gonna try and recreate dash work in streamlit
"""


from math import ceil
from pyparsing import And
import streamlit as st
import pandas as pd
import json
import requests
import numpy as np
import plotly.express as px

st. set_page_config(layout="wide")

st.image('fpl.png', use_column_width=True)

st.title('FPL App')



