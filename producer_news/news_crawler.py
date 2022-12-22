import json
import logging
import requests
import time
import numpy as np
import pandas as pd

from datetime import datetime as dt
from datetime import timedelta
from bs4 import BeautifulSoup
from pytz import timezone
from kafka import KafkaProducer


logging.basicConfig(
    format=(
        '%(asctime)s %(levelname)-8s[%(lineno)s: %(funcName)s] %(message)s'
    )
)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


SLEEP_TIME = 43200  # 12 hours
TOPIC_NAME = 'newssink'
KAFKA_BROKER_URL = 'broker:9092'


def GetDataframe(soup, newsPage):
    # create empty array
    headLineArray = []

    if newsPage == 'TASS':
        # use for loop to write quotes in quotes_text with append
        for i in soup.find('div', {'class': 'news-list-content__news-block'}).find_all("div", {"class": "news-content news-content_default"}):
            storyTitle = i.find('span', {'class':'news-content__title'})
            timeStamp = i.find('div', {'class':'news-content__date'}).find('dateformat').get("time")
            href = "https://tass.com" + i.find('a', href=True).get("href")

            if(storyTitle is None):
                storyTitle = None
            else:
                storyTitle = storyTitle.text
            if(timeStamp is None):
                timeStamp = None
            else:
                timeStamp = time.ctime(int(timeStamp))
            if(href is None):
                href = None

            headLineArray.append([storyTitle, timeStamp, href])

        dataframe = pd.DataFrame(headLineArray, columns=["Title", "Time", "Link"])

        # data cleanup
        dataframe["Title"] = dataframe["Title"].str.replace("\n\t\t\t\t\t\t\t\t", "")

        dataframe['Time'] = pd.to_datetime(dataframe['Time'])
        dataframe['Time'][1].replace(tzinfo=timezone('UTC'))
        return  dataframe

    elif newsPage == 'REUTERS':
        # use for loop to write quotes in quotes_text with append
        for i in soup.find('div', {'class': 'column1 col col-10'}).find_all("div", {"class": "story-content"}):
            storyTitle = i.find('h3', {'class':'story-title'})
            timeStamp = i.find('span', {'class':'timestamp'})
            href = "https://www.reuters.com" + i.find('a', href=True).get("href")

            if(storyTitle is None):
                storyTitle = None
            else:
                storyTitle = storyTitle.text
            if(timeStamp is None):
                timeStamp = None
            else:
                timeStamp = timeStamp.text
            if(href is None):
                href = None

            headLineArray.append([storyTitle, timeStamp, href])

        dataframe = pd.DataFrame(headLineArray, columns=["Title", "Time", "Link"])
        now_EST = dt.today().astimezone(timezone('EST'))
        # data cleanup
        dataframe["Title"] = dataframe["Title"].str.replace("\n\t\t\t\t\t\t\t\t", "")
        dataframe["Time"]  = dataframe['Time'].apply(lambda x: (str(now_EST.month) + "/" + str(now_EST.day) + "/" + str(now_EST.year) + " " + x.replace(" EST", "")) if x != None else np.nan)
        #convert time to utc
        dataframe['Time'] = pd.to_datetime(dataframe['Time'], format='%m/%d/%Y %I:%M%p')
        dataframe['Time'] = dataframe['Time'] + timedelta(hours = 5)
        return dataframe

    elif newsPage == 'UKRINFORM':
        # skip first entry

        # use for loop to write quotes in quotes_text with append
        for i in soup.find_all('article'):
            storyTitle = i.find('h2').find('a')
            timeStamp = i.find('time').get('datetime')
            href = "https://www.ukrinform.net" + i.find('h2').find('a').get("href")

            if(storyTitle is None):
                storyTitle = None
            else:
                storyTitle = storyTitle.text
            if(timeStamp is None):
                timeStamp = None
            if(href is None):
                href = None

            headLineArray.append([storyTitle, timeStamp, href])
        dataframe = pd.DataFrame(headLineArray, columns=["Title", "Time", "Link"])
        # data cleanup
        dataframe['Time'] = pd.to_datetime(dataframe['Time'], format="%Y-%m-%dT%H:%M:%S%z")
        dataframe['Time'] = pd.to_datetime(dataframe['Time'], format='%m/%d/%Y %I:%M%p')
        dataframe['Time'] = dataframe['Time'].apply(lambda x: x.replace(tzinfo=None) if x != None else x)
        return dataframe

    elif newsPage == 'THE_MOSCOW_TIMES':
        # use for loop to write quotes in quotes_text with append
        for i in soup.find('div', {'class': 'sidebar__sticky'}).find_all("li", {"class": "listed-articles__item"}):
            storyTitle = i.find('h5', {'class':'article-excerpt-tiny__headline'})
            timeStamp = i.find('time', {'class':'article-excerpt-tiny__time'}).get("datetime")
            href = i.find('a', href=True).get("href")

            if(storyTitle is None):
                storyTitle = None
            else:
                storyTitle = storyTitle.text
            if(timeStamp is None):
                timeStamp = None
            if(href is None):
                href = None

            headLineArray.append([storyTitle, timeStamp, href])
        dataframe = pd.DataFrame(headLineArray, columns=["Title", "Time", "Link"])
        # data cleanup
        dataframe["Title"] = dataframe["Title"].str.replace("\n\t\t\t", "")
        dataframe['Time'] = pd.to_datetime(dataframe['Time'], format="%Y-%m-%dT%H:%M:%S%z")
        dataframe['Time'] = dataframe['Time'].apply(lambda x: x.replace(tzinfo=None) if x != None else x)
        return dataframe


# Get HeadlineDataFromNewsPage
def GetHeadlineDataFromNewsPage(newsPage):
    if newsPage == 'TASS': #TASS # Pro Russia
        URL = 'https://tass.com/ukraine'
    elif newsPage == 'THE_MOSCOW_TIMES': #THE_MOSCOW_TIMES # Pro Russia
        URL = 'https://www.themoscowtimes.com/ukraine-war'
    elif newsPage == 'REUTERS': #REUTERS # Pro Ukrain
        URL = 'https://www.reuters.com/news/archive/ukraine'
    elif newsPage == 'UKRINFORM': #UKRINFORM # Pro Ukrain
        URL = 'https://www.ukrinform.net/block-lastnews'
    else:
        return None

    # requests
    html = requests.get(URL)
    html.status_code
    soup = BeautifulSoup(html.text, 'html.parser')

    dataframe = GetDataframe(soup, newsPage)
    
    return json.loads(dataframe.to_json(orient='records'))


def main():

    producer = KafkaProducer(
        bootstrap_servers=KAFKA_BROKER_URL,
        value_serializer=lambda x: json.dumps(x).encode('utf8'),
        api_version=(0, 10, 1)
    )

    news_sources = {
        'THE_MOSCOW_TIMES',
        'UKRINFORM',
        'REUTERS',
        'TASS'
    }

    while True:
        for source in news_sources:

            result = GetHeadlineDataFromNewsPage(source)
            logger.info("Found %s articles for source %s" % (len(result), source))

            for article in result:
                data = {
                    'title': article['Title'],
                    'url': article['Link'],
                    'created_at': str(dt.fromtimestamp(float(article['Time']) / 1000.0))
                }

                producer.send(TOPIC_NAME, value=data)
            time.sleep(2)

        logger.info("Scrape complete, waiting for %s hours" % (SLEEP_TIME / 60 / 60))
        time.sleep(SLEEP_TIME)


if __name__ == '__main__':
    main()
