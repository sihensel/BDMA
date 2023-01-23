import dash
from dash import html, dcc, Input, Output, callback, dash_table

import plotly.express as px
from plotly.graph_objs import Layout, Figure

from datetime import datetime as dt
from datetime import date
import pandas as pd
import time

import geopandas as gpd
import pyproj
import getgraphs
import dash_bootstrap_components as dbc


# Self written
#from textmining import GetTopHashtagsData, GetTopWordsData

from utils import load_from_cassandra

### import data ### 

# import data from cassandra
df_twitter = load_from_cassandra("twitter")
df_news = load_from_cassandra("news")

# uncomment for local testing
# df_twitter = pd.read_csv("././dashboard/data/twitter_labeled.csv", on_bad_lines='skip')

df_twitter.created_at = pd.to_datetime(df_twitter.created_at)
# -----------------#

# -----------------#

dash.register_page(__name__, path='/rawTweetsData')

### dropdown menue ### 

### create Layout ### 

BOX_STYLE  = {
    "padding-top": "10px",
    "margin-top": "5px",
    "margin-bottom": "5px",
    "margin-left": "5px",
    "margin-right": "5px",
    "border-radius": "5px",
    "color": "white",
    "background-color": "#13173C"
}

DROPDOWN_STYLE  = {
    "margin-top": "10px",
    "margin-bottom": "10px",
    "margin-left": "5px",
    "margin-right": "5px",
    "border-radius": "5px",
    "color": "black",
    "background-color": "#13173C",
    "padding": "10px",
}

layout =     html.Div([

                dbc.Row([dbc.Col(html.Div(html.Div(id="raw_data_tweets")))], style=BOX_STYLE),

                html.P(id = 'dummy-input'),
                ], className='reload')

# # -----------------#
# Callbacks

# Callback 1
@callback(
    Output(component_id='raw_data_tweets', component_property='children'),

    Input(component_id='dummy-input', component_property='value')


)
def update_rawDataTweets(dummy_input):
    return getgraphs.GetRawData(df_twitter) #html.Div(dash_table.DataTable(df_news.to_dict('records'), [{"name": i, "id": i} for i in df_news.columns]))


# -----------------#

