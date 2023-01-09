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

df_news['urlMarkDown'] = df_news['url'].apply(lambda x: "<a href='" + x + "' target='_blank'>Link</a>" if str(x) != None else "")

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

dateselection = [
    'date selection'
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
        html.Div(id='top'),
        # Navigation Bar
        html.Div(
            [
            dcc.Dropdown(id='hashtag-options', 
                         options=hashtags,
                         value=hashtags[0],
                         placeholder='Please select a hashtag...', 
                         ),
            dcc.Dropdown(dateselection,
                         placeholder='Date',
                         disabled = True,
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
            html.Div([
            html.A("Real and Fake Histogram", href='#top'),
            html.Hr(),
            html.A("Tweets Table", href='#section-two'),
            html.Hr(),
            html.A("Textmining", href="#section-three"),
            html.Hr(),
            html.A("News Article", href="#section-four"),
            html.Hr(),
            html.A("History of fake tweets", href="#section-five")

            ], className='side-bar-menue')
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
                                html.P(f'''Unverfied users count'''),
                                html.P(id='verfiedFakeUsersValue', style={'font-size': '25px'}),
                        ]
                        , className="figure-real-fake-tweets-info-left"
                    ),
                    html.Div(
                        [
                                html.P(f'''Verfied users count'''),
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
        html.Div(id='section-two'),
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
                                style={'color':'black', 'height':'0px'}
                                ),
                                dcc.Input(id="tweetSearch", type="text", placeholder="Search Tweets", style={'marginRight':'10px'}),
                                html.Div(html.Div(id='fake-tweets-list'), style={'position':'relative', 'top': '65px', 'z-index':'2'})
                                
                            ],
                                className="fake-tweets-div"
                    ),
                    html.Div(id='section-three'),
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
                                style={'color':'black', 'height':'40px'}
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
                                style={'color':'black', 'height':'40px'}
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
        html.Div(id='section-four'),
        html.Div([
            html.Div(
                [
                    html.Div(
                            [
                                html.P(f'''Pro Russian News'''),
                                dcc.Dropdown(id='proRussiaNewsToggleInput', 
                                options=proRussianNewsToggle,
                                value=proRussianNewsToggle[0], 
                                style={'color':'black', 'height':'0px'}
                                ),
                                html.Div(html.Div(id='russiaNewsList'), style={'position':'relative', 'top': '50px', 'z-index':'2'})
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
                                style={'color':'black', 'height':'0px'}
                                ),             
                                html.Div(html.Div(id='ukraineNewsList'), style={'position':'relative', 'top': '50px', 'z-index':'2'})
                            ],
                                className="news-div-right", style={'margin-left': '1%'}
                    ),
                ],
                className= "news-info-container-right"
            )
        ], className = 'figure-container-fourth', id="newsArticle-id"),
        # Graphical Container Div the five
        html.Div(id='section-five'),
        html.Div([
            # History of face Tweets
            html.Div(
                [
                    html.Div(
                            [
                                html.P(f'''Account creation date of users posting fake tweets'''),
                                dcc.Dropdown(id='fakeReal-date-tweets-input', 
                                options=fakeRealToggle,
                                value=fakeRealToggle[0], 
                                style={'color':'black', 'height':'0px'}
                                ),
                                html.Div(dcc.Graph(id='histogram-fake-authors'), style={'position':'relative', 
                                                                                        'top': '40px', 'height': '450px'}),
                                dcc.RangeSlider(min=2007, max=2023,value=[2019,2023], step=1, marks=None,
                                            tooltip={"placement": "bottom", "always_visible": True}, id='dateSlider-input',)
                            ], style={'height': '540px'},
                                className="fake-tweets-div"
                    ), 
                ], style={'height': '580px'},
                className= "fake-tweets-info-container"
            ),
        ]
        , className ='figure-container-second', style= {'margin-top': '40px'}
        ),
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
    Output('histogram-fake-authors', 'figure'),

    Input('tweetSearch', 'value'),
    Input('hashtag-options', 'value'),
    Input('fakeReal-tweets-input', 'value'),
    Input('hashtags-slider-input', 'value'),
    Input('fakeReal-hashtag-input', 'value'),
    Input('words-slider-input', 'value'),
    Input('fakeReal-words-input', 'value'),
    Input('proRussiaNewsToggleInput', 'value'),
    Input('proUkraineNewsToggleInput', 'value'),
    Input('fakeReal-date-tweets-input', 'value'),
    Input('dateSlider-input', 'value')



)
def set_hashtag(tweetSearch,
                hashtag, 
                fakeRealTweets, 
                sliderHashtagsValue, 
                fakeRealHashtag, 
                sliderWordsValue, 
                fakeRealWords, 
                proRussiaNewsToggleInput,
                proUkraineNewsToggleInput,
                fakeRealDateTweetsInput,
                dateSliderInput):

    
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
    if(tweetSearch != None):
        df_temp3 = df_temp3[df_temp3['tweet'].str.contains(str(tweetSearch).lower())]

    fakeTweetDiv = html.Div(
        children=[
            dash_table.DataTable(df_temp3[['tweet']].to_dict('records'),[{"name": i, "id": i} for i in df_temp3[['tweet']]], 
            style_header={'display': 'none'},
            style_table={'height': '330px', 'width':'90%', 'overflowY': 'auto',  'left': '5%', 'position': 'relative'},
            style_data={
                'whiteSpace': 'normal',
                'height': 'auto',
                'textAlign': 'left',
                'color': 'white',
                'background': 'black',
                'font-size': '17px',
                'backgroundColor': 'rgba(0,0,0,0)'
         }, 
         page_size=25,
          )
            ],
        )

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
        children=[dash_table.DataTable(
        data    = df_russianNews[['title', 'urlMarkDown']].to_dict('records'),
        columns = [{'id': i, 'name': i, 'presentation': 'markdown'} if i == 'urlMarkDown' else {"name": i, "id": i, 'presentation': 'markdown'} for i in df_russianNews.loc[:,['title', 'urlMarkDown']]],
        markdown_options={"html": True},
        style_header={'display': 'none'},
        style_table={'height': '330px', 'width':'90%', 'overflowY': 'auto',  'left': '5%','display': 'inline-block'},
        style_data={
            'whiteSpace': 'normal',
            'height': 'auto',
            'textAlign': 'left',
            'color': 'white',
            'background': 'black',
            'font-size': '17px',
            'backgroundColor': 'rgba(0,0,0,0)'
    }, 
    style_cell_conditional=[
        {'if': {'column_id': 'title'},
         'width': '80%'},
        {'if': {'column_id': 'urlMarkdown'},
         'width': '20%'},
    ],
    page_size=25,
    )
    ])

    df_ukrainNews = df_news[df_news['NewsSource']==str(proUkraineNewsToggleInput)]

    ukrainNewsList =  html.Div(
        children=[dash_table.DataTable(
            data    = df_ukrainNews[['title', 'urlMarkDown']].to_dict('records'),
            columns = [{'id': i, 'name': i, 'presentation': 'markdown'} if i == 'urlMarkDown' else {"name": i, "id": i, 'presentation': 'markdown'} for i in df_ukrainNews.loc[:,['title', 'urlMarkDown']]],
            markdown_options={"html": True},
            style_header={'display': 'none'},
            style_table={'height': '330px', 'width':'90%', 'overflowY': 'auto',  'left': '5%', 'display': 'inline-block'},
            style_data={
            'whiteSpace': 'normal',
            'height': 'auto',
            'textAlign': 'left',
            'color': 'white',
            'background': 'black',
            'font-size': '17px',
            'backgroundColor': 'rgba(0,0,0,0)'
            
    }, 
    style_cell_conditional=[
        {'if': {'column_id': 'title'},
         'width': '80%'},
        {'if': {'column_id': 'urlMarkdown'},
         'width': '20%'},
    ],
    page_size=25,
    )
    ])

    df_author = df_twitter[df_twitter["tweet"].str.contains(hashtag.lower())]
    df_author = df_author[df_author["label"].str.match(fakeRealDateTweetsInput)]
    df_author['author_create_at_year_month'] = df_author['author_created_at'].apply(lambda x: x[0:7]if x != None else "")
    df_author = df_author["author_create_at_year_month"].value_counts()
    df_author = df_author.rename_axis('author_create_at_year_month').to_frame('count')
    df_author.reset_index(level=0, inplace=True)
    df_author['author_created_at_year'] =  df_author['author_create_at_year_month'].apply(lambda x: int(x[0:4]) if x != None else 0)

    author_date_users_posting_fake_tweets = px.bar(
        df_author[(df_author['author_created_at_year'] >= dateSliderInput[0]) & (df_author['author_created_at_year'] <= dateSliderInput[1])],
        x="author_create_at_year_month",
        y="count",
        color="count",
        height=440,
    ).update_layout(
        xaxis_title="Date",
        yaxis_title="Count",
        paper_bgcolor = 'rgba(0,0,0,0)',
        plot_bgcolor = 'rgba(0,0,0,0)',
        font_color="white"
    )

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
                \
            author_date_users_posting_fake_tweets
                
                

# -----------------#

if __name__ == '__main__':
    app.run_server(debug=False)