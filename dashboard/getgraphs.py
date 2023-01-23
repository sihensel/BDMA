import geopandas as gpd
import pyproj
import pandas as pd
import plotly.express as px
import re
import nltk
from nltk.tokenize import RegexpTokenizer
from nltk.probability import FreqDist
from nltk.corpus import stopwords
from dash import html, dash_table
        
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import LatentDirichletAllocation

def df_name_count(df, name):
    return df[df["tweet"].str.contains(name)].shape[0]


def GetUkraineMap(data, map_df):
    capitalListEN = [   "cherkasy",
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

    indexValue = 1
    df_ukraine_count = pd.DataFrame(columns=['index', 'name', 'count'])
    for name in capitalListEN:
        df_ukraine_count.loc[len(df_ukraine_count.index)] =  [indexValue, name,df_name_count(data, name)]
        indexValue += 1


    # reading in the shapefile
    map_df.to_crs(pyproj.CRS.from_epsg(4326), inplace=True)

    merged = map_df#.set_index('District').join(df.set_index('District'))
    #merged = merged.reset_index()

    merged['count'] = df_ukraine_count['count']

    figures = px.choropleth(merged, 
                        geojson=merged.geometry, 
                        locations=merged.index,
                        color='count',
                        hover_data=["name:en"],
                        )
    figures.update_geos(fitbounds="locations", 
                    visible=False)
    figures.update_layout(paper_bgcolor ='rgba(0,0,0,0)', geo_bgcolor='rgba(0,0,0,0)', showlegend=False)
    return figures

def GetHistCities(data, map_df):
    capitalListEN = [   "cherkasy",
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

    indexValue = 1
    df_ukraine_count = pd.DataFrame(columns=['index', 'name', 'count'])
    for name in capitalListEN:
        df_ukraine_count.loc[len(df_ukraine_count.index)] =  [indexValue, name,df_name_count(data, name)]
        indexValue += 1


    # reading in the shapefile
    map_df.to_crs(pyproj.CRS.from_epsg(4326), inplace=True)

    merged = map_df#.set_index('District').join(df.set_index('District'))
    #merged = merged.reset_index()

    merged['count'] = df_ukraine_count['count']
    merged['name_short'] = capitalListEN

    figure = px.histogram(
            merged.sort_values(by='count', ascending=False)[0:10],
            y="name_short",
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

def GetTotalTweets(data):
    return data.shape[0]

def GetFakeTweets(data):
    return data[data['label'] == 'fake'].count()[0]

def GetTotalProUkraineArticles(data):
    return data.shape[0]

def GetTotalProRussiaArticles(data):
    return data.shape[0]

def GetPieFakeNews(data):
    if(data is not None):
        if(data.shape[0] < 2):
            return px.pie()
        fig = px.pie(data.groupby('label')['label'].count(), values='label', names=['real', 'fake'])
        fig.update_layout(
                paper_bgcolor = 'rgba(0,0,0,0)',
                plot_bgcolor = 'rgba(0,0,0,0)',
                font_color="white")
        return fig
    return None

def GetTopHashtagsData(df_temp1, topCommonCount):
    df_hashtags = df_temp1['tweet'].reset_index()

    regexp = RegexpTokenizer(r'#\w+')

    df_hashtags['clean_text']=df_hashtags['tweet'].apply(lambda x: re.sub(r"#+\w+", "", x))

    df_hashtags['hashtags']=df_hashtags['tweet'].apply(regexp.tokenize)

    # stopwords = [hashtag[1:]]

    # df_hashtags['hashtags'] = df_hashtags['hashtags'].apply(lambda x: [i for i in x if i not in stopwords])

    df_hashtags['hashtags_joined'] = df_hashtags['hashtags'].apply(lambda x: ' '.join([i for i in x]))

    all_words = ' '.join([i for i in df_hashtags['hashtags_joined']])

    words_tokens = (regexp.tokenize(all_words))

    fd = FreqDist(words_tokens)

    top_10 = fd.most_common(topCommonCount)

    df_dist = pd.DataFrame(top_10, columns=['hashtag', 'count'])

    return df_dist


def GetTopWordsData(df_temp1, topCommonCount):
    stopwords = nltk.corpus.stopwords.words("english")
    df_hashtags = df_temp1['tweet'].reset_index()

    regexp = RegexpTokenizer(r'\w+')

    df_hashtags['clean_text']=df_hashtags['tweet'].apply(lambda x: re.sub(r"#+\w+", "", x))

    df_hashtags['hashtags']=df_hashtags['tweet'].apply(regexp.tokenize)
    df_hashtags['hashtags'] = df_hashtags['hashtags'].apply(lambda x: [i for i in x if i not in stopwords])
    # stopwords = [hashtag[1:]]

    # df_hashtags['hashtags'] = df_hashtags['hashtags'].apply(lambda x: [i for i in x if i not in stopwords])

    df_hashtags['hashtags_joined'] = df_hashtags['hashtags'].apply(lambda x: ' '.join([i for i in x]))

    all_words = ' '.join([i for i in df_hashtags['hashtags_joined']])

    words_tokens = (regexp.tokenize(all_words))

    fd = FreqDist(words_tokens)

    top_10 = fd.most_common(topCommonCount)

    df_dist = pd.DataFrame(top_10, columns=['hashtag', 'count'])

    return df_dist

def GetTopHashtags(data):
    topWordsData = (GetTopHashtagsData(data, int(10)))
    fig = px.histogram(
        topWordsData,
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
    return fig


def GetTopWords(data):
    topWordsData = (GetTopWordsData(data, int(10)))
    fig = px.histogram(
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
    return fig

def GetTweets(data, fakeReal_tweets_input):
    if (fakeReal_tweets_input == 'all'):
        pass
    else:
        data = data[(data["label"] == fakeReal_tweets_input)]
    data = data[:10]
    child = html.Div(
        children=[
            dash_table.DataTable(
            data    = data[['tweet', 'urlMarkDown']].to_dict('records'),
            columns = [{'id': i, 'name': i, 'presentation': 'markdown'} if i == 'urlMarkDown' else {"name": i, "id": i, 'presentation': 'markdown'} for i in data.loc[:,['tweet', 'urlMarkDown']]],
            markdown_options={"html": True},
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
    return child


def GetNewsList(data):
    return html.Div(
        children=[dash_table.DataTable(
        data    = data[['title', 'urlMarkDown']].to_dict('records'),
        columns = [{'id': i, 'name': i, 'presentation': 'markdown'} if i == 'urlMarkDown' else {"name": i, "id": i, 'presentation': 'markdown'} for i in data.loc[:,['title', 'urlMarkDown']]],
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

def GetTweetCount(data, range):
    data['year'] = pd.to_datetime(data['created_at']).dt.year
    data['month'] = pd.to_datetime(data['created_at']).dt.month
    data['day'] = pd.to_datetime(data['created_at']).dt.day
    data['hour'] = pd.to_datetime(data['created_at']).dt.hour

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

def GetRawData(data):
    child = html.Div(
        children=[
            dash_table.DataTable(data.to_dict('records'),[{"name": i, "id": i} for i in data], 
            style_table={'width':'90%', 'overflowY': 'auto',  'left': '5%', 'position': 'relative'},
            style_data={
                'whiteSpace': 'normal',
                'height': 'auto',
                'textAlign': 'left',
                'color': 'white',
                'background': 'black',
                'font-size': '17px',
                'backgroundColor': 'rgba(0,0,0,0)',
                'backgroundColor': 'rgba(0,0,0,0)'
         },     style_header={
        'backgroundColor': 'rgba(0,0,0,0)',
        'color': 'white',
        'fontWeight': 'bold'
    },
    style_filter={
        'backgroundColor': 'rgba(40, 44, 84, 1)',
        'color': 'white'
    },
    filter_action="native",
    filter_options={"placeholder_text": "Filter column..."},
         page_size=300,
          )
            ],
        )
    return child


def GetTopicModelling(data):
    stopwords = nltk.corpus.stopwords.words("english")
    # Load Dataset
    df_twitter_sized = data[:500]
    df_twitter_sized['clean_text']=df_twitter_sized['tweet'].apply(lambda x: re.sub(r"#+\w+", "", x))
    documents_list= df_twitter_sized['tweet'].tolist()

    # Initialize regex tokenizer
    tokenizer = RegexpTokenizer(r'\w+')
    stopwords.append('ukraine')
    stopwords.append('russia')
    stopwords.append('ukrainerussianwar')
    stopwords.append('ukrainerussiawar')
    stopwords.append('standwithukraine')
    stopwords.append('ukrainewar')
    stopwords.append('ukrainenazis')


    tfidf = TfidfVectorizer(lowercase=True,
                            stop_words = stopwords,
                            ngram_range = (1,1),
                            tokenizer = tokenizer.tokenize)

    train_data = tfidf.fit_transform(documents_list) 

    num_components=5

    model=LatentDirichletAllocation(n_components=num_components)

    lda_matrix = model.fit_transform(train_data)
 
    lda_components=model.components_

    terms = tfidf.get_feature_names_out()

    topicList = []
    for index, component in enumerate(lda_components):
        zipped = zip(terms, component)
        top_terms_key=sorted(zipped, key = lambda t: t[1], reverse=True)[:7]
        top_terms_list=list(dict(top_terms_key).keys())
        topicList.append(top_terms_list )

    df = pd.DataFrame({'topics':topicList})

    return html.Div(
        children=[dash_table.DataTable(
        data    = df[['topics']].to_dict('records'),
        columns = [{'id': i, 'name': i, 'presentation': 'markdown'} if i == 'urlMarkDown' else {"name": i, "id": i, 'presentation': 'markdown'} for i in df.loc[:,['topics']]],
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

