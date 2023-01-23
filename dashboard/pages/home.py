import dash
from dash import html, dcc, Input, Output, callback

import plotly.express as px
from plotly.graph_objs import Layout, Figure

from datetime import datetime as dt
from datetime import date
import pandas as pd

import geopandas as gpd
import getgraphs
import dash_bootstrap_components as dbc

# Self written
#from textmining import GetTopHashtagsData, GetTopWordsData

# from utils import load_from_cassandra

### import data ### 

# import data from cassandra
# df_twitter = load_from_cassandra("twitter")
# df_news = load_from_cassandra("news")

# uncomment for local testing
df_twitter = pd.read_csv("././dashboard/data/twitter_labeled.csv", on_bad_lines='skip')
df_news = pd.read_csv("././dashboard/data/news.csv", on_bad_lines='skip')

df_twitter = df_twitter[df_twitter['tweet'] != "real"]
df_twitter = df_twitter[df_twitter['tweet'] != "fake"]


fp = r"C:\Users\Sven\Downloads\ukraine_geojson-master\ukraine_geojson-master\UA_FULL_Ukraine.json"
df_map = gpd.read_file(fp)

df_twitter.created_at = pd.to_datetime(df_twitter.created_at)
df_news.created_at = pd.to_datetime(df_news.created_at)    

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

df_twitter['urlMarkDown'] = df_twitter['id'].apply(lambda x: "<a href='https://twitter.com/default/status/" + str(x) + "' target='_blank'>Link</a>" if str(x) != None else "")
# -----------------#

dash.register_page(__name__, path='/')

### dropdown menue ### 

hashtags = [
    'All Tweets',
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
    'all',
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

capitalListEN = [   "All Tweets",
                    "cherkasy",
                    "chernihiv",
                    "chernivtsi",
                    "crimea",
                    "dnipropetrovsk",
                    "donetsk",
                    "ivano-frankivsk",
                    "kharkiv",
                    "kherson",
                    "khmelnytskyi",
                    "kiev",
                    "kirovohrad",
                    "luhansk",
                    "lviv",
                    "mykolaiv",
                    "odessa",
                    "poltava",
                    "rivne",
                    "sumy",
                    "ternopil",
                    "vinnytsia",
                    "volyn",
                    "zakarpattia",
                    "zaporizhia",
                    "zhytomyr" ]

### create Layout ### 

def GetDatePicker(id_name):
    return dcc.DatePickerRange(
                    id=id_name,
                    min_date_allowed=date(2022, 12, 24),
                    max_date_allowed=date(2023, 1, 24),
                    initial_visible_month=date(2022, 12, 25),
                    end_date=date(2023, 1, 23)
                )

def GetSingleDatePicker(id_name):
    return dcc.DatePickerSingle(
                    id=id_name,
                    min_date_allowed=date(2022, 12, 24),
                    max_date_allowed=date(2023, 1, 24),
                    initial_visible_month=date(2022, 12, 25),
                    date=date(2023, 1, 23)
                )


def GetTimePicker(id_name):
    return dcc.Input(id=id_name, type='time')

def GetGraph(title, id_name, class_name):
    return html.Div(
        [
            html.Div(
                        [
                            html.P(title),
                            dcc.Graph(id=id_name)
                        ],
                            className=class_name
                    ),
        ]
    )

def GetNavBar(id_name):
    return html.Div(
                    [
                    ], style = BOX_STYLE,
                        )


def GetDropDownCities(id_name):
    return html.Div(
                [
                dcc.Dropdown(id=id_name, 
                            options=capitalListEN,
                            value=capitalListEN[0],
                            placeholder='Please select a hashtag...', 
                            )]
                    )

def GetNumberDiv(title, id_name, class_name):
    return html.Div(
                        [
                                html.P(title),
                                html.P(id=id_name, style={'font-size': '30px'}),
                        ]
                        , className=class_name
                    )

def GetTweetsSearch(title, id_name, class_name):
    # Real and fake tweets Figure
    return        html.Div(
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
                                html.Div(html.Div(id='fake-tweets-list'))
                            ],
                                className="fake-tweets-div"
                    ),
                    html.Div(id='section-three'),
                ],
                className= "fake-tweets-info-container"
            )

def GetNewsArticle(title, id_name, drop_down_array, list_id):
    return html.Div(
                        [
                            html.P(title),
                            dcc.Dropdown(id=id_name, 
                            options=drop_down_array,
                            value=drop_down_array[0], style={'color': 'black'}
                            ),
                            html.Div(html.Div(id=list_id))
                        ]
                    )

NAVBAR_STYLE = {
    "background-color": "#13173C",
    "border-radius": "5px",
    "border-color": "white",
    "text-align": "auto",
    "position": "fixed",
    "z-index": "5",
    "margin-top": "-27px",
}

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

NAV_STYLE  = {
    "margin-left": "-5px",
    "border-radius": "5px",
    "color": "black",
    "border-color": "white",
    "background-color": "#13173C",
    "position": "fixed",
    "width": "77.5%",
    "margin-top": "-10px",
    "z-index": "5",
    "padding": "10px",
    "border-width": "5px"
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

                dbc.Row([
                                dbc.Col(dcc.Dropdown(id='drop-down-hashtags', 
                                    options=hashtags,
                                    style={'height': '15px'},
                                    value=hashtags[0],
                                    placeholder='Please select a hashtag...'), width=3),
                                dbc.Col(dcc.RadioItems(['day', 'span'], 'span', style={'color': 'white'}, id='day-span-picker'), width=1),
                                dbc.Col(GetSingleDatePicker('my-date-picker-range-from'),width=2),
                                dbc.Col([dcc.Input(type='number', min=0, max=23, step=1, id='time-from'),dcc.Input(type='number', min=0, max=23, step=1, id='time-till')], width=2),
                                dbc.Col(GetDatePicker('my-date-picker-range'),width=4) ], style=NAV_STYLE),

                dbc.Row([
                    dbc.Col(style={'margin-top': '75px'})
                ]),
                    dbc.Row([
                            dbc.Col(GetGraph('Ukraine Map', 'ukraine-map', 'two-third'), width=7, style=BOX_STYLE),
                            dbc.Col(GetGraph('Top Cities', 'top-cities-barChart', 'one-third'), width=4, style=BOX_STYLE)
                        ], align='center'),
                    dbc.Row(dbc.Col([GetDropDownCities('drop-down-cities')], style=DROPDOWN_STYLE)),
                    
                    dbc.Row(
                        [
                            dbc.Col(GetNumberDiv('Total Tweets', 'total-tweets', 'first'), style=BOX_STYLE),
                            dbc.Col(GetNumberDiv('Detected Fake News', 'detected-fake-news', 'second'), style=BOX_STYLE),
                            dbc.Col(GetNumberDiv('Pro Ukraine Article Count', 'pro-ukraine-count', 'third'), style=BOX_STYLE),
                            dbc.Col(GetNumberDiv('Pro Russia Article Count', 'pro-russia-count', 'fourth'), style=BOX_STYLE),
                        ]
                    ),
                    dbc.Row(
                        [
                            dbc.Col(GetGraph(r'% of fake tweets', 'fake-tweets-pie-chart', 'one-third'),width=3,  style=BOX_STYLE),
                            dbc.Col(GetTweetsSearch('','',''), style=BOX_STYLE)
                        ]),
                    # GetGraph('Top Topics', 'top-topics-barChart', 'one-third'),
                    dbc.Row(
                        [
                  dbc.Col(GetNewsArticle('Pro Russian News', 'pro-Russia-News-Toggle-Input', proRussianNewsToggle, 'russian-news-list'), style=BOX_STYLE),
                  dbc.Col(GetNewsArticle('Pro Ukraine News', 'pro-Urkaine-News-Toggle-Input', proUkrainNewsToggle, 'ukraine-news-list'), style=BOX_STYLE),
                        ], justify="between"
                ),
                dbc.Row(
                        [
                            dbc.Col(GetGraph('Top News Words', 'top-topics-barChart', 'one-third'), width = 5,style=BOX_STYLE),
                            dbc.Col(html.Div([html.P("Topics"), html.Div(id='topic-modell')]), width = 6,style=BOX_STYLE)
                        ]
                ),
                dbc.Row(
                        [
                            dbc.Col(GetGraph('Top Words', 'top-words-barChart', 'one-third'),style=BOX_STYLE),
                            dbc.Col(GetGraph('Top hashtags', 'top-hashtags-barChart', 'one-third'), style=BOX_STYLE)
                        ], justify="between"
                ),
                dbc.Row([
                         dbc.Col(
                            html.Div(
                                    [
                                        html.Div(
                                                    [
                                                        html.P("Tweet Count and Topics"),
                                                        dcc.Dropdown(id='tweet-count-with-topic-drop-down-time', 
                                                        options=['month', 'day', 'hour'],
                                                        value=['month', 'day', 'hour'][1], style={'color': 'black'}
                                                        ),
                                                        dcc.Graph(id="tweet-count-with-topic-lineChart")
                                                    ]
                                                ),
                                    ]
                                    )   
                                ,style=BOX_STYLE
                                )
                        ],

                ),
            #    GetGraph('Account Creation Dates', 'account-creation-date-barChart', 'full-width'),

                html.P(id = 'dummy-input'),
                ], className='reload')

# # -----------------#
# Callbacks

# Callback 1
@callback(
    Output(component_id='ukraine-map', component_property='figure'),
    Output(component_id='top-cities-barChart', component_property='figure'),
    Output(component_id='total-tweets', component_property='children'),
    Output(component_id='detected-fake-news', component_property='children'),
    Output(component_id='pro-ukraine-count', component_property='children'),
    Output(component_id='pro-russia-count', component_property='children'),
    Output(component_id='fake-tweets-pie-chart', component_property='figure'),
    Output(component_id='top-topics-barChart', component_property='figure'),
    Output(component_id='top-words-barChart', component_property='figure'),
    Output(component_id='top-hashtags-barChart', component_property='figure'),
    Output(component_id='fake-tweets-list', component_property='children'),
    Output(component_id='russian-news-list', component_property='children'),
    Output(component_id='ukraine-news-list', component_property='children'),
    Output(component_id='tweet-count-with-topic-lineChart', component_property='figure'),
    Output(component_id='topic-modell', component_property='children'),


    Input(component_id='dummy-input', component_property='value'),
    Input(component_id='drop-down-hashtags', component_property='value'),
    Input(component_id='my-date-picker-range', component_property='start_date'),
    Input(component_id='my-date-picker-range', component_property='end_date'),
    Input(component_id='drop-down-cities', component_property='value'),
    Input(component_id='pro-Russia-News-Toggle-Input', component_property='value'),
    Input(component_id='pro-Urkaine-News-Toggle-Input', component_property='value'),
    Input(component_id='tweet-count-with-topic-drop-down-time', component_property='value'),
    Input(component_id='fakeReal-tweets-input', component_property='value'),
    Input(component_id='day-span-picker', component_property='value'),
    Input(component_id='my-date-picker-range-from', component_property='date'),
    Input(component_id='time-from', component_property='value'),
    Input(component_id='time-till', component_property='value'),


)
def update_dashboard(dummy_input, drop_down_hashtags, start_date, end_date,  drop_down_cities, russiaArticleToggle, ukraineArticleToggle, tweetCountDropDown, fakeReal_tweets_input, day_time_picker, single_date, hour_from, hour_till):
    dateTime = df_twitter
    dateTimeArticle = df_news
    
    if(day_time_picker == 'day'):
        if single_date is not None:
            date_object = pd.to_datetime(single_date)
            if(single_date is not None):
                dateTime = dateTime[(dateTime['created_at'].dt.year == date_object.year) & (dateTime['created_at'].dt.month == date_object.month) & (dateTime['created_at'].dt.day == date_object.day)]
                dateTimeArticle = dateTimeArticle[(dateTimeArticle['created_at'].dt.year == date_object.year) & (dateTimeArticle['created_at'].dt.month == date_object.month) & (dateTimeArticle['created_at'].dt.day == date_object.day)]
                if((hour_from is not None) & (hour_till is not None)):
                    if((hour_from < hour_till)):
                        dateTime = dateTime[(dateTime['created_at'].dt.hour >= hour_from) & (dateTime['created_at'].dt.hour <= hour_till)]
                        dateTimeArticle = dateTimeArticle[(dateTimeArticle['created_at'].dt.hour >= hour_from) & (dateTimeArticle['created_at'].dt.hour <= hour_till)]

    elif(day_time_picker == 'span'):
        if start_date is not None:
            start_date_object = pd.to_datetime(start_date)

        if end_date is not None:
            end_date_object = pd.to_datetime(end_date)
            if(start_date is not None):
                dateTime = dateTime[(dateTime['created_at'].dt.tz_localize(None) <= end_date_object) & (dateTime['created_at'].dt.tz_localize(None) >= start_date_object)]
                dateTimeArticle = dateTimeArticle[(dateTimeArticle['created_at'] <= end_date_object) & (dateTimeArticle['created_at'] >= start_date_object)]
        
    dateTimeArticleHashtagsRussia = dateTimeArticle[(dateTimeArticle['NewsSource'].str.contains("TASS")) | (dateTimeArticle['NewsSource'].str.contains("TheMoscowTimes"))]
    dateTimeArticleHashtagsUkraine = dateTimeArticle[(dateTimeArticle['NewsSource'].str.contains("Ukrinform")) | (dateTimeArticle['NewsSource'].str.contains("Reuters"))]

    dateTimeArticleRussiaToggle = dateTimeArticleHashtagsRussia[dateTimeArticleHashtagsRussia['NewsSource']==str(russiaArticleToggle)]
    dateTimeArticleUkraineToggle = dateTimeArticleHashtagsUkraine[dateTimeArticleHashtagsUkraine['NewsSource']==str(ukraineArticleToggle)]
    dataHashtags = dateTime
    if (drop_down_hashtags == hashtags[0]):
        dataHashtags = dateTime
    else:
        dataHashtags = dateTime[dateTime["tweet"].str.contains(drop_down_hashtags.lower())]
    dataCities = dataHashtags
    if (drop_down_cities == capitalListEN[0]):
        dataCities = dataHashtags
    else:
        dataCities = dataHashtags[dataHashtags["tweet"] == drop_down_cities]

    return getgraphs.GetUkraineMap(dataHashtags, df_map), \
           getgraphs.GetHistCities(dataHashtags, df_map), \
           getgraphs.GetTotalTweets(dataCities), \
           getgraphs.GetFakeTweets(dataCities), \
           getgraphs.GetTotalProUkraineArticles(dateTimeArticleHashtagsUkraine), \
           getgraphs.GetTotalProRussiaArticles(dateTimeArticleHashtagsRussia), \
           getgraphs.GetPieFakeNews(dataCities), \
           getgraphs.GetTopWords(dateTimeArticle.rename(columns = {'title':'tweet'})), \
           getgraphs.GetTopWords(dataCities), \
           getgraphs.GetTopHashtags(dataCities), \
           getgraphs.GetTweets(dataCities, fakeReal_tweets_input), \
           getgraphs.GetNewsList(dateTimeArticleRussiaToggle),\
           getgraphs.GetNewsList(dateTimeArticleUkraineToggle),\
           getgraphs.GetTweetCount(dataCities, tweetCountDropDown), \
           getgraphs.GetTopicModelling(dataCities)


# -----------------#

