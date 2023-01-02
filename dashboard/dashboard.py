import plotly.express as px
from dash import Dash, dcc, html, Input, Output

from utils import load_from_cassandra


app = Dash(__name__)

# import data from cassandra
df_twitter = load_from_cassandra("twitter")
df_news = load_from_cassandra("news")

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
    html.H2('Data'),
    html.Div([
        html.Div([
            dcc.Dropdown(hashtags, id='hashtag-options'),
            dcc.Graph(id='histogram-label')
        ], style={'width': '35%', 'display': 'inline-block'}),

        html.Div([
            dcc.Graph(id='histogram-verified')
        ], style={'width': '35%', 'display': 'inline-block'}),
    ]),

    html.Div([
        dcc.Graph(id='plot-cross')
    ], style={'width': '35%', 'display': 'inline-block'}),

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
    Output('article-title', 'children'),
    Output('article-url', 'href'),
    Input('hashtag-options', 'value')
)
def set_hashtag(hashtag):

    if hashtag:
        df_temp = df_twitter[df_twitter["tweet"].str.contains(hashtag.lower())]
        df_temp2 = df_temp[df_temp["label"].str.match("fake")]
    else:
        # use all data when no hashtag is selected
        df_temp = df_twitter
        df_temp2 = df_twitter

    fig1 = px.histogram(
        df_temp,
        x="label"
    ).update_layout(
        title="Real and Fake Tweets",
        xaxis_title="Label",
        yaxis_title="No. of Tweets",
    )

    fig2 = px.histogram(
        df_temp,
        x="author_verified"
    ).update_layout(
        title="Verified and Unverified Users",
        xaxis_title="Label",
        yaxis_title="No. of Tweets",
    )

    fig3 = px.histogram(
        df_temp2,
        x="author_verified"
    ).update_layout(
        title="Verified and Unverified Users of Fake Tweets",
        xaxis_title="Label",
        yaxis_title="No. of Tweets",
    )

    # only display the first value for now
    title = " - " + df_news["title"].iloc[0]
    url = df_news["url"].iloc[0]

    return fig1, fig2, fig3, title, url


if __name__ == '__main__':
    app.run_server(host='0.0.0.0', debug=False)
