from math import ceil
from pyparsing import And
import streamlit as st
import pandas as pd
import json
import requests
import numpy as np
import plotly.express as px

st.image('fpl.png', use_column_width=True)


# base url for all FPL API endpoints
base_url = "https://fantasy.premierleague.com/api/"
end_point = "https://fantasy.premierleague.com/api/fixtures/"

# get data from bootstrap-static endpoint
r = requests.get(base_url + end_point, verify=False).json()

# get player data from 'elements' field
players = pd.json_normalize(r["elements"])
teams = pd.json_normalize(r["teams"])

# Subset data
players_sub = players[
]