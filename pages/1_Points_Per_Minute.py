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
import plotly.io as pio

st.image('fpl.png', use_column_width=True)


# base url for all FPL API endpoints
base_url = "https://fantasy.premierleague.com/api/"

# get data from bootstrap-static endpoint
r = requests.get(base_url + "bootstrap-static/", verify=False).json()

# get player data from 'elements' field
players = pd.json_normalize(r["elements"])
teams = pd.json_normalize(r["teams"])

# Subset data
players_sub = players[
    [
        "web_name",
        "team",
        "element_type",
        "now_cost",
        "minutes",
        "total_points",
        "goals_scored",
        "assists",
        "clean_sheets",
        "bps",
    ]
]

# Merge players with teams
players_sub = players_sub.merge(teams[["id", "name", 'played']], left_on="team", right_on="id")
players_sub["team"] = players_sub["name"]
del players_sub["name"]

# Calculate points per minute
players_sub["ppm"] = players_sub["total_points"].astype(float) / players_sub["minutes"].astype(float)
# Set nan and inf values to 0
players_sub["ppm"] = players_sub["ppm"].replace([np.nan, -np.inf], 0)
# Set ppm to 0 if the player has played under 5 full games in the season
# or has played in less than 1/3 of their teams games
players_sub.loc[
    (
        (
            (players_sub["minutes"] < 90*1) |
            (
                players_sub['minutes'].astype(float) < (players_sub['played'].astype(float)/3 * 90)
            )
        )
        , "ppm"
    ) 
] = 0


# Def fig 1
fig = px.bar(
    players_sub.sort_values(["team", "ppm"], axis=0, ascending=True),
    x="team",
    y="total_points",
    color="ppm",
    barmode="group",
    hover_name="web_name",
    hover_data=["minutes"],
    # range_color=(0, 0.1),
    width=800,
    labels={
        "team": "Team Name",
        "total_points": "Total Points",
        "ppm": "Points per Minute",
        "web_name": "Name",
        "minutes": "Minutes Played",
        'played': 'Games played'
    },
    color_continuous_scale="viridis",
)
fig.update_layout(
    yaxis=dict(
        gridcolor='gray',
        griddash = 'dash'
    ),
    # Set plot background colour
    plot_bgcolor = '#0e1117',
    paper_bgcolor = '#0e1117'
)

fig.update_traces(
    marker_line_color='black',
    marker_line_width = 0.5
)

# Display fig 1
st.header = 'Best value players:'
st.plotly_chart(fig, use_container_width=True)
    

# Data manipulation for team breakdown
graph_data = players_sub.sort_values(["element_type"], axis=0, ascending=True)
# Map position type
pos_dict = {1: "GK", 2: "DEF", 3: "MID", 4: "ATT"}
graph_data["element_type"] = graph_data["element_type"].replace(pos_dict)

# # def fig 2
col1, col2, col3 = st.columns(3)
with col1:
    team = st.multiselect('Select teams:', list(graph_data["team"].unique()), default=['Man Utd'])
with col2:
    position = st.multiselect('Select positions:', list(graph_data["element_type"].unique()), default=['GK', 'DEF', 'MID', 'ATT'])
with col3:
    ppm_slider = st.slider('PPM Range:', min_value=0.0, max_value= ceil(100*(graph_data['ppm'].max()))/100, value = (0.0,ceil(100*(graph_data['ppm'].max()))/100),step=0.005)
    
fig_2 = px.scatter(
    graph_data.loc[(graph_data["team"].isin(team)) 
                   & (graph_data["element_type"].isin(position))
                   & (graph_data["ppm"] >= ppm_slider[0])
                   & (graph_data["ppm"] <= ppm_slider[1])],
    x="total_points",
    y="now_cost",
    symbol="element_type",
    hover_name="web_name",
    hover_data=["minutes"],
    labels={
        "now_cost": "Price",
        "element_type": "Position Type",
        "total_points": "Total Points",
        "ppm": "Points per Minute",
        "web_name": "Name",
        "minutes": "Minutes Played",
        'played': 'Games played'
    },
    size="minutes",
    color="ppm",
    color_continuous_scale="viridis",
    range_color=(0, 0.1),
    size_max=20,
    color_discrete_map={
        "GK": "rgba(239,187,82,1)",
        "DEF": "rgba(97,176,229,1)",
        "MID": "rgba(137,188,86,1)",
        "ATT": "rgba(240,127,127,1)",
    })

# 
fig_2.update_layout(
    legend=dict(
        orientation="h", yanchor="bottom", x=0.15, y=-0.25, font=dict(size=14)
    )
)

if len(team) > 0:
    with st.container():
        st.plotly_chart(fig_2, use_container_width=True)
    
