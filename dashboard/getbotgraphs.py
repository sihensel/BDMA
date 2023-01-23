from dash import Dash, dcc, html, Input, Output, dash_table
import plotly.express as px
from plotly.graph_objs import Layout, Figure
import plotly.graph_objects as go

from datetime import datetime as dt
import pandas as pd


def GetSentimentGaug(data, value):
    if (value == "all"):
        pass
    elif(value == "bot"):
        data = data[data['bot'] == 1.0]
    elif(value == "no_bot"):
        data = data[data['bot'] == 0.0]

    fig = go.Figure(go.Indicator(
        domain = {'x': [0, 1], 'y': [0, 1]},
        value = data.compound.mean(),
        mode = "gauge+number",
        title = {'text': "Sentiment"},
        gauge = {'axis': {'range': [-1, 1]},
                'steps' : [
                    {'range': [-1, 0], 'color': "pink"},
                    {'range': [0, 1], 'color': "lightgreen"}],
                'threshold' : {'line': {'color': "red", 'width': 4}, 'thickness': 0.75, 'value': 0}}))
    fig.update_layout(paper_bgcolor = "rgba(0,0,0,0)", font = {'color': "white", 'family': "Arial"})
    return fig

def GetBotsCount(data):
    return data[data['bot'] == 1.0].count()[0]
    

def GetAccountCreatedAt(data, range):
    data['year'] = pd.to_datetime(data['author_created_at']).dt.year
    data['month'] = pd.to_datetime(data['author_created_at']).dt.month
    data['day'] = pd.to_datetime(data['author_created_at']).dt.day
    data['hour'] = pd.to_datetime(data['author_created_at']).dt.hour

    if(range == 'month'):
        df_time = pd.DataFrame(data.groupby([data['year'], data['month']])['month'].agg({'count'}).reset_index())
        df_time['datetime'] = pd.to_datetime(df_time['year'].astype(str)  + "-" +  df_time['month'].astype(str), format='%Y-%m')
    elif(range == 'day'):
        df_time = pd.DataFrame(data.groupby([data['year'], data['month'], data['day']])['day'].agg({'count'}).reset_index())
        df_time['datetime'] = pd.to_datetime(df_time['year'].astype(str)  + "-" +  df_time['month'].astype(str) + "-" +  df_time['day'].astype(str), format='%Y-%m-%d')
    elif(range == 'hour'):
        df_time = pd.DataFrame(data.groupby([data['year'], data['month'], data['day'], data['hour']])['hour'].agg({'count'}).reset_index())
        df_time['datetime'] = pd.to_datetime(df_time['year'].astype(str)  + "-" +  df_time['month'].astype(str) + "-" +  df_time['day'].astype(str) + "-" +  df_time['hour'].astype(str) , format='%Y-%m-%d-%H')

    fig = px.line(df_time, x="datetime", y="count")
    fig.update_xaxes(rangeslider_visible=True)
    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Count",
        paper_bgcolor = 'rgba(0,0,0,0)',
        plot_bgcolor = 'rgba(0,0,0,0)',
        font_color="white"
    )
    return fig

def GetPieBotChart(data):

    if(data is not None):
        if(data.shape[0] < 2):
            return px.pie()
        df = pd.DataFrame()
        df["countdata"] = data.bot.value_counts()
        df = df.reset_index()
        df = df.append({'index': 'NaN', 'countdata': data['bot'].isna().sum()}, ignore_index = True)
        fig = px.pie(df, values='countdata', names=['1', '0', 'NaN'])
        fig.update_layout(
                paper_bgcolor = 'rgba(0,0,0,0)',
                plot_bgcolor = 'rgba(0,0,0,0)',
                font_color="white")
        return fig
    return None

def GetHistAuthorLocation(data):
    bot_df = pd.DataFrame(data.groupby('author_location')['author_location'].agg({'count'})).sort_values('count', ascending=False).reset_index()

    figure = px.histogram(
            bot_df.sort_values(by='count', ascending=False)[0:10],
            y="author_location",
            x="count",
            color="count"
        ).update_layout(
            xaxis_title="Tweet count",
            yaxis_title="Cities",
            paper_bgcolor = 'rgba(0,0,0,0)',
            plot_bgcolor = 'rgba(0,0,0,0)',
            font_color="white",
        ).update_yaxes(categoryorder='total ascending')

    return figure