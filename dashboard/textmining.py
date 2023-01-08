from dash import Dash, dcc, html, Input, Output, dash_table
import plotly.express as px
from plotly.graph_objs import Layout, Figure
from datetime import datetime as dt
import pandas as pd
import nltk
from nltk.tokenize import RegexpTokenizer
from nltk.probability import FreqDist
import time
import re

def GetTopHashtagsData(df_temp1, hashtag, topCommonCount):
    df_hashtags = df_temp1['tweet'].reset_index()

    regexp = RegexpTokenizer(r'#\w+')

    df_hashtags['hashtags']=df_hashtags['tweet'].apply(regexp.tokenize)

    stopwords = [hashtag]

    df_hashtags['hashtags'] = df_hashtags['hashtags'].apply(lambda x: [i for i in x if i not in stopwords])

    df_hashtags['hashtags_joined'] = df_hashtags['hashtags'].apply(lambda x: ' '.join([i for i in x]))

    all_words = ' '.join([i for i in df_hashtags['hashtags_joined']])

    words_tokens = (regexp.tokenize(all_words))

    fd = FreqDist(words_tokens)

    top_10 = fd.most_common(topCommonCount)

    df_dist = pd.DataFrame(top_10, columns=['hashtag', 'count'])

    rankHistogram = px.histogram(
            df_dist,
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
    return df_dist

def GetTopWordsData(df_temp1, hashtag, topCommonCount):
    df_hashtags = df_temp1['tweet'].reset_index()

    regexp = RegexpTokenizer(r'\w+')

    df_hashtags['clean_text']=df_hashtags['tweet'].apply(lambda x: re.sub(r"#+\w+", "", x))

    df_hashtags['hashtags']=df_hashtags['tweet'].apply(regexp.tokenize)

    stopwords = [hashtag[1:]]

    df_hashtags['hashtags'] = df_hashtags['hashtags'].apply(lambda x: [i for i in x if i not in stopwords])

    df_hashtags['hashtags_joined'] = df_hashtags['hashtags'].apply(lambda x: ' '.join([i for i in x]))

    all_words = ' '.join([i for i in df_hashtags['hashtags_joined']])

    words_tokens = (regexp.tokenize(all_words))

    fd = FreqDist(words_tokens)

    top_10 = fd.most_common(topCommonCount)

    df_dist = pd.DataFrame(top_10, columns=['hashtag', 'count'])

    return df_dist