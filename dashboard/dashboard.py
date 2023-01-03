import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output
from datetime import datetime as dt

from utils import load_from_cassandra


def extract_date(date_str: str):
    """ Extract year-month from a date string """
    date = dt.strptime(date_str, '%Y-%m-%dT%H:%M:%S.%fZ').date()
    return "%s-%s" % (date.year, date.month)


app = Dash(__name__)

# import data from cassandra
df_twitter = load_from_cassandra("twitter")
df_news = load_from_cassandra("news")

# local testing
# df_twitter = pd.read_csv("~/twitter_labeled.csv")
# df_news = pd.read_csv("~/news.csv")

# transform the date format into'year-month'
df_twitter["author_created_at"] = df_twitter["author_created_at"].apply(lambda x: extract_date(x))

hashtags = [
    '#Ukraine',
    '#UkraineWar',
    '#UkraineNazis',
    '#UkraineRussianWar',
    '#RussianWarCrimes',
    '#UkraineRussiaWar',
    '#RussiaIsATerroristState'
]

# build the page layout
app.layout = html.Div([
    html.H2('Twitter fake news dashboard'),
    html.Div([
        html.P("Please select a hashtag below."),
        dcc.Dropdown(hashtags, hashtags[0], id='hashtag-options'),
        html.Div([
            dcc.Graph(id='histogram-label')
        ], style={'width': '35%', 'display': 'inline-block'}),

        html.Div([
            dcc.Graph(id='histogram-verified')
        ], style={'width': '35%', 'display': 'inline-block'}),
    ]),

    html.Div([
        html.Div([
            dcc.Graph(id='plot-cross')
        ], style={'width': '35%', 'display': 'inline-block'}),

        html.Div([
            dcc.Graph(id='plot-author-created')
        ], style={'width': '35%', 'display': 'inline-block'}),
    ]),

    html.Hr(),

    html.Div([
        html.H2('News Articles'),
        dcc.Link(
            "Link",
            id='article-url',
            href="",
            target="_blank"
        ),
        html.Span(id='article-title'),
    ])
])


@app.callback(
    Output('histogram-label', 'figure'),
    Output('histogram-verified', 'figure'),
    Output('plot-cross', 'figure'),
    Output('plot-author-created', 'figure'),
    Output('article-title', 'children'),
    Output('article-url', 'href'),
    Input('hashtag-options', 'value')
)
def set_hashtag(hashtag):

    df_temp = df_twitter[df_twitter["tweet"].str.contains(hashtag.lower())]
    df_temp2 = df_temp[df_temp["label"].str.match("fake")]

    uniques = df_temp2["author_created_at"].value_counts()
    df_temp3 = uniques.rename_axis('author_created_at').to_frame('count')
    df_temp3.reset_index(level=0, inplace=True)

    fig1 = px.histogram(
        df_temp,
        x="label"
    ).update_layout(
        title="Real and fake tweets",
        xaxis_title="Label",
        yaxis_title="No. of Tweets",
    )

    fig2 = px.histogram(
        df_temp,
        x="author_verified"
    ).update_layout(
        title="Verified and unverified users",
        xaxis_title="Label",
        yaxis_title="No. of Tweets",
    )

    fig3 = px.histogram(
        df_temp2,
        x="author_verified"
    ).update_layout(
        title="Verified and unverified users of fake tweets",
        xaxis_title="Label",
        yaxis_title="No. of Tweets",
    )

    fig4 = px.bar(
        df_temp3,
        x="author_created_at",
        y="count"
    ).update_layout(
        title="Account creation date of users posting fake tweets",
        xaxis_title="Date",
        yaxis_title="Count",
    )

    # only display the first value for now
    title = " - " + df_news["title"].iloc[0]
    url = df_news["url"].iloc[0]

    return fig1, fig2, fig3, fig4, title, url


if __name__ == '__main__':
    app.run_server(host='0.0.0.0', debug=False)
