from dash import Dash, dcc, html, Input, Output, dash_table
import plotly.express as px
from plotly.graph_objs import Layout, Figure

from datetime import datetime as dt
import pandas as pd
import time

# Self written
# from FuncWordcloud import GetWordCloud
from textmining import GetTopHashtagsData, GetTopWordsData

### import data ### 

# import data from cassandra
# df_twitter = load_from_cassandra("twitter")
# df_news = load_from_cassandra("news")

# local testing
df_twitter = pd.read_csv("./dashboard/data/twitter_labeled.csv")
df_news = pd.read_csv("./dashboard/data/news.csv")

# -----------------#

newsSourceList = []
for index, row in df_news.iterrows():
    if(row['url'].startswith('https://tass.com')):
        newsSourceList.append('TASS')
    elif(row['url'].startswith('https://www.themoscowtimes.com')):
        newsSourceList.append('TheMoscowTimes')
        row['title'] = row['title'][:-4]
    elif(row['url'].startswith('https://www.ukrinform.net')):
        newsSourceList.append('Ukrinform')
    elif(row['url'].startswith('https://www.reuters.com')):
        newsSourceList.append('Reuters')
    else:
        newsSourceList.append('NaN')

df_news['NewsSource'] = newsSourceList

# -----------------#

def extract_date(date_str: str):
    """ Extract year-month from a date string """
    date = dt.strptime(date_str, '%Y-%m-%dT%H:%M:%S.%fZ').date()
    return "%s-%s" % (date.year, date.month)


app = Dash(__name__)

### dropdown menue ### 

hashtags = [
    '#Ukraine',
    '#UkraineWar',
    '#UkraineNazis',
    '#UkraineRussianWar',
    '#RussianWarCrimes',
    '#UkraineRussiaWar',
    '#RussiaIsATerroristState'
]

language = [
    'English',
    'German'
]

fakeRealToggle = [
    'fake',
    'real'
]

proRussianNewsToggle = [
    'TASS',
    'TheMoscowTimes'
]

proUkrainNewsToggle = [
    'Reuters',
    'Ukrinform'
]

### create Layout ### 

app.layout = html.Div(
    [
        # Navigation Bar
        html.Div(
            [
            dcc.Dropdown(id='hashtag-options', 
                         options=hashtags,
                         value=hashtags[0],
                         placeholder='Please select a hashtag...', 
                         ),
            dcc.Dropdown(language,
                         'English',
                         id='language-options', 
                         ),
            html.Div
            (
            [
                html.Div(id='nav-time')
            ],className='app-nav-time'
            )
            ]
            , className="app-nav-bar"
        ),

        # Side Bar

        html.Div([
            html.P(f'''Dashboard'''),
            html.A("Real and Fake Histogram", href='#histogram-label'),
            html.Hr(),
            html.A("Tweets Table", href='#fakeReal-tweets-input'),
            html.Hr(),
            html.A("Textmining", href="#textmining-id"),
            html.Hr(),
            html.A("News Article", href="#newsArticle-id"),
            ]
            ,className="side-bar"
        ),

        # Graphical Container Div
        html.Div([
            # Real and fake tweets Figure
            html.Div(
                [
                    html.Div(
                            [
                                html.P(f'''Real and fake tweets'''),
                                dcc.Graph(id='histogram-label')
                            ],
                                className="figure-real-fake-tweets"
                    ),
                    html.Div(
                        [
                                html.P(f'''Real tweets count'''),
                                html.P(id='realTweetValue', style={'font-size': '25px'}),
                        ]
                        , className="figure-real-fake-tweets-info-left"
                    ),
                    html.Div(
                        [
                                html.P(f'''Fake tweets count'''),
                                html.P(id='fakeTweetValue', style={'font-size': '25px'}),
                        ]
                        , className="figure-real-fake-tweets-info-right"
                    )
                ],
                className= "figure-real-fake-tweets-container"
            ),

            # vertified
            html.Div(
                [
                    html.Div(
                            [
                                html.P(f'''Verified and unverified users''', id='container'),
                                dcc.Graph(id='verifiedFigure')
                            ],
                                className="verified-figure-info"
                    ),
                    html.Div(
                        [
                                html.P(f'''Unverfied users count'''),
                                html.P(id='unverfiedUsersValue', style={'font-size': '25px'}),
                        ]
                        , className="figure-real-fake-tweets-info-left"
                    ),
                    html.Div(
                        [
                                html.P(f'''Verfied users count'''),
                                html.P(id='verfiedUsersValue', style={'font-size': '25px'}),
                        ]
                        , className="figure-real-fake-tweets-info-right"
                    )
                ],
                className= "verified-figure-info-container"

            ),

            # fakeReviews verfied and unverified
            html.Div(
                [
                    html.Div(
                            [
                                html.P(f'''Verified and unverified users of fake tweets'''),
                                dcc.Graph(id='verifiedFakeFigure')
                            ],
                                className="verified-fake-figure-info"
                    ),
                    html.Div(
                        [
                                html.P(f'''Verfied users count'''),
                                html.P(id='verfiedFakeUsersValue', style={'font-size': '25px'}),
                        ]
                        , className="figure-real-fake-tweets-info-left"
                    ),
                    html.Div(
                        [
                                html.P(f'''Unverfied users count'''),
                                html.P(id='unverfiedFakeUsersValue', style={'font-size': '25px'}),
                        ]
                        , className="figure-real-fake-tweets-info-right"
                    )
                ],
                className= "verified-fake-figure-info-container"
            )
        ]
        , className = 'figure-container-first'
        ),

        # Graphical Container Div the Second
        html.Div([
            # Real and fake tweets Figure
            html.Div(
                [
                    html.Div(
                            [
                                html.P(f'''Tweets'''),
                                dcc.Dropdown(id='fakeReal-tweets-input', 
                                options=fakeRealToggle,
                                value=fakeRealToggle[0], 
                                style={'color':'black'}
                                ),
                                html.Div(html.Div(id='fake-tweets-list'), style={'position':'relative', 'top': '-250px', 'z-index':'2'})
                                
                            ],
                                className="fake-tweets-div"
                    ),
                ],
                className= "fake-tweets-info-container"
            ),
        ]
        , className ='figure-container-second'
        ),
    # Graphical Container Div the Third
        html.Div([
            html.Div(
                [
                    html.Div(
                            [
                                html.P(f'''Top Hashtags also used'''),
                                dcc.Dropdown(id='fakeReal-hashtag-input', 
                                options=fakeRealToggle,
                                value=fakeRealToggle[0], 
                                style={'color':'black'}
                                ),
                                dcc.Slider(10, 20, 1, value=10, marks=None,
                                            tooltip={"placement": "bottom", "always_visible": True},
                                            id='hashtags-slider-input'),
                                
                                

                                dcc.Graph(id='fake-tweets-top-hashtags', style={'top': '50px'})
                            ],
                                className="fake-tweets-top-hashtags-div"
                    ),
                ],
                className= "fake-tweets-top-hashtags-info-container", id="textmining-id"
            ),
            html.Div(
                [
                    html.Div(
                            [
                                html.P(f'''Top Words used'''),
                                dcc.Dropdown(id='fakeReal-words-input', 
                                options=fakeRealToggle,
                                value=fakeRealToggle[0], 
                                style={'color':'black'}
                                ),
                                dcc.Slider(10, 20, 1, value=10, marks=None,
                                            tooltip={"placement": "bottom", "always_visible": True},
                                            id='words-slider-input'),
                                
                                
                                dcc.Graph(id='fake-tweets-top-words', style={'top': '50px'})
                            ],
                                className="fake-tweets-top-hashtags-div", style={'margin-left': '1%'}
                    ),
                ],
                className= "fake-tweets-top-hashtags-info-container"
            )
        ], className = 'figure-container-third'),
        # Graphical Container Div the Fourth
        html.Div([
            html.Div(
                [
                    html.Div(
                            [
                                html.P(f'''Pro Russian News'''),
                                dcc.Dropdown(id='proRussiaNewsToggleInput', 
                                options=proRussianNewsToggle,
                                value=proRussianNewsToggle[0], 
                                style={'color':'black'}
                                ),
                                html.Div(html.Div(id='russiaNewsList'), style={'position':'relative', 'top': '-270px', 'z-index':'2'})
                            ],
                                className="news-div-left"
                    ),
                ],
                className= "news-info-container"
            ),
            html.Div(
                [
                    html.Div(
                            [
                                html.P(f'''Pro Ukrain News'''),
                                dcc.Dropdown(id='proUkraineNewsToggleInput', 
                                options=proUkrainNewsToggle,
                                value=proUkrainNewsToggle[0], 
                                style={'color':'black'}
                                ),             
                                html.Div(html.Div(id='ukraineNewsList'), style={'position':'relative', 'top': '-270px', 'z-index':'2'})
                            ],
                                className="news-div-right", style={'margin-left': '1%'}
                    ),
                ],
                className= "news-info-container-right"
            )
        ], className = 'figure-container-fourth', id="newsArticle-id")
    ]
)

# -----------------#
# Callbacks

@app.callback(
    Output('nav-time', 'children'),

    Output('histogram-label', 'figure'),
    Output('realTweetValue', 'children'),
    Output('fakeTweetValue', 'children'),

    Output('verifiedFigure', 'figure'),
    Output('unverfiedUsersValue', 'children'),
    Output('verfiedUsersValue', 'children'),

    Output('verifiedFakeFigure', 'figure'),
    Output('unverfiedFakeUsersValue', 'children'),
    Output('verfiedFakeUsersValue', 'children'),

    Output('fake-tweets-list', 'children'),
    Output('fake-tweets-top-hashtags', 'figure'),
    Output('fake-tweets-top-words', 'figure'),

    Output('russiaNewsList', 'children'),
    Output('ukraineNewsList', 'children'),

    Input('hashtag-options', 'value'),
    Input('fakeReal-tweets-input', 'value'),
    Input('hashtags-slider-input', 'value'),
    Input('fakeReal-hashtag-input', 'value'),
    Input('words-slider-input', 'value'),
    Input('fakeReal-words-input', 'value'),
    Input('proRussiaNewsToggleInput', 'value'),
    Input('proUkraineNewsToggleInput', 'value'),



)
def set_hashtag(hashtag, 
                fakeRealTweets, 
                sliderHashtagsValue, 
                fakeRealHashtag, 
                sliderWordsValue, 
                fakeRealWords, 
                proRussiaNewsToggleInput,
                proUkraineNewsToggleInput):

    
    curr_time =     html.P(f'''{time.strftime("%H:%M %d.%m.%Y", time.localtime())}''')


    df_temp = df_twitter[df_twitter["tweet"].str.contains(hashtag.lower())]

    realFakeTweets = px.histogram(
        df_temp,
        x="label",
        color="label"
    ).update_layout(
        xaxis_title="Label",
        yaxis_title="No. of Tweets",
        paper_bgcolor = 'rgba(0,0,0,0)',
        plot_bgcolor = 'rgba(0,0,0,0)',
        font_color="white",
    )
    realTweetValue = df_temp[df_temp['label'] == 'real'].count()
    fakeTweetValue = df_temp[df_temp['label'] == 'fake'].count()

    verifiedFigure = px.histogram(
        df_temp,
        x="author_verified",
        color="author_verified"
    ).update_layout(
        xaxis_title="Label",
        yaxis_title="No. of Users",
        paper_bgcolor = 'rgba(0,0,0,0)',
        plot_bgcolor = 'rgba(0,0,0,0)',
        font_color="white",
    )
    verfiedUsersValue = df_temp[df_temp['author_verified'] == True].count()
    unverfiedUsersValue = df_temp[df_temp['author_verified'] == False].count()

    df_temp2 = df_temp[df_temp["label"].str.match("fake")]

    verifiedFakeFigure = px.histogram(
        df_temp2,
        x="author_verified",
        color="author_verified"
    ).update_layout(
        xaxis_title="Verified and unverified users of fake tweets",
        yaxis_title="No. of Users",
        paper_bgcolor = 'rgba(0,0,0,0)',
        plot_bgcolor = 'rgba(0,0,0,0)',
        font_color="white"
    )
    
    unverfiedFakeUsersValue = df_temp2[df_temp2['author_verified'] == False].count()
    verifiedFakeFigureUsersValue = df_temp2[df_temp2['author_verified'] == True].count()

    df_temp3 = df_temp[(df_temp["label"] == fakeRealTweets)]

    fakeTweetDiv = html.Div(
        children=[
            dash_table.DataTable(df_temp3[['tweet']].to_dict('records'),[{"name": i, "id": i} for i in df_temp3[['tweet']]], 
            style_header={'display': 'none'},
            style_table={'height': '330px', 'width':'90%', 'overflowY': 'auto',  'left': '5%', 'position': 'relative'},
            style_data={
                'whiteSpace': 'normal',
                'height': 'auto',
                'textAlign': 'left',
                'color': 'grey',
                'background': 'black',
                'font-size': '17px',
                'backgroundColor': 'rgba(0,0,0,0)'
         }, 
         page_size=25,
          )
            ],
        )
    # encoded_image = base64.b64encode(open(GetWordCloud(df_temp3), 'rb').read())
    # fakeTweetWordCloudDiv = html.Div([html.Img(src='data:image/png;base64,{}'.format(encoded_image.decode()))])
    topHashtagsDataToggle = df_temp[(df_temp["label"] == fakeRealHashtag)]
    
    topHashtagsData = (GetTopHashtagsData(topHashtagsDataToggle, hashtag.lower(), sliderHashtagsValue))

    topHashtagsFigure = px.histogram(
            topHashtagsData,
            y="hashtag",
            x="count",
            color="count"
        ).update_layout(
            xaxis_title="Hashtag count",
            yaxis_title="Hashtags",
            paper_bgcolor = 'rgba(0,0,0,0)',
            plot_bgcolor = 'rgba(0,0,0,0)',
            font_color="white",
        ).update_yaxes(categoryorder='total ascending')

    topWordsDataToggle = df_temp[(df_temp["label"] == fakeRealWords)]

    topWordsData = (GetTopWordsData(topWordsDataToggle, hashtag.lower(), int(sliderWordsValue)))

    topWordsFigure = px.histogram(
            topWordsData,
            y="hashtag",
            x="count",
            color="count"
        ).update_layout(
            xaxis_title="Word count",
            yaxis_title="Words",
            paper_bgcolor = 'rgba(0,0,0,0)',
            plot_bgcolor = 'rgba(0,0,0,0)',
            font_color="white",
        ).update_yaxes(categoryorder='total ascending')

    df_russianNews = df_news[df_news['NewsSource']==str(proRussiaNewsToggleInput)]

    russianNewsList =  html.Div(
        children=[dash_table.DataTable(df_russianNews[['title']].to_dict('records'),[{"name": i, "id": i} for i in df_russianNews[['title', 'created_at']]], 
        style_header={'display': 'none'},
        style_table={'height': '330px', 'width':'90%', 'overflowY': 'auto',  'left': '5%','display': 'inline-block'},
        style_data={
            'whiteSpace': 'normal',
            'height': 'auto',
            'textAlign': 'left',
            'color': 'grey',
            'background': 'black',
            'font-size': '17px',
            'backgroundColor': 'rgba(0,0,0,0)'
    }, 
    page_size=25,
    )
    ])

    df_ukrainNews = df_news[df_news['NewsSource']==str(proUkraineNewsToggleInput)]

    ukrainNewsList =  html.Div(
        children=[dash_table.DataTable(
            data    = df_ukrainNews[['title', 'url']].to_dict('records'),
            columns = [{'id': i, 'name': i} if i == 'url' else {"name": i, "id": i} for i in df_ukrainNews.loc[:,['title', 'url']]], # 'presentation': 'markdown'
            markdown_options={"html": True},
            style_header={'display': 'none'},
            style_table={'height': '330px', 'width':'90%', 'overflowY': 'auto',  'left': '5%', 'display': 'inline-block'},
            style_data={
            'whiteSpace': 'normal',
            'height': 'auto',
            'textAlign': 'left',
            'color': 'grey',
            'background': 'black',
            'font-size': '17px',
            'backgroundColor': 'rgba(0,0,0,0)'
    }, 
    style_cell={
        'maxWidth': 5
    },
    page_size=25,
    )
    ])

    return  curr_time, \
                \
            realFakeTweets, \
            realTweetValue[0], \
            fakeTweetValue[0], \
                \
            verifiedFigure, \
            unverfiedUsersValue[0], \
            verfiedUsersValue[0], \
                \
            verifiedFakeFigure, \
            verifiedFakeFigureUsersValue[0], \
            unverfiedFakeUsersValue[0], \
                \
            fakeTweetDiv, \
            topHashtagsFigure, \
            topWordsFigure,\
                \
            russianNewsList, \
            ukrainNewsList, \
                
                

# -----------------#

if __name__ == '__main__':
    app.run_server(debug=True)