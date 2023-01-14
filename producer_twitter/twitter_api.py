import json
import logging
import re
import requests
import time

from tweepy import Client
from kafka import KafkaProducer

from keys import bearer_token, consumer_key, consumer_secret, access_token, access_token_secret


logging.basicConfig(
    format=(
        '%(asctime)s %(levelname)-8s[%(lineno)s: %(funcName)s] %(message)s'
    )
)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

SLEEP_TIME = 10800

# Kafka settings
TOPIC_NAME = 'twitter'
KAFKA_BROKER_URL = 'broker:9092'


def main():

    producer = KafkaProducer(
        bootstrap_servers=KAFKA_BROKER_URL,
        value_serializer=lambda x: json.dumps(x).encode('utf8'),
        api_version=(0, 10, 1)
    )

    client = Client(
        bearer_token=bearer_token,
        consumer_key=consumer_key,
        consumer_secret=consumer_secret,
        access_token=access_token,
        access_token_secret=access_token_secret,
        return_type=requests.Response,
        wait_on_rate_limit=True
    )

    hashtags = {
        '#Ukraine',
        '#UkraineWar',
        '#UkraineNazis',
        '#UkraineRussianWar',
        '#RussianWarCrimes',
        '#UkraineRussiaWar',
        '#RussiaIsATerroristState'
    }

    logger.info("Getting Tweets from Twitter API")

    ids = set()
    while True:
        for tag in hashtags:
            logger.info("Scraping hashtag %s" % tag)
            response = client.search_recent_tweets(
                '%s lang:en -is:retweet -is:quote -is:reply' % tag,
                tweet_fields=[
                    'author_id',
                    'created_at',
                    'lang',
                    'public_metrics'
                ],
                expansions=['author_id'],
                user_fields=['verified', 'created_at', 'public_metrics', 'location'],
                max_results=100
            ).json()

            tweets = response['data']
            users = response['includes']['users']

            for tweet in tweets:

                if tweet['id'] in ids:
                    logger.debug("Duplicate Tweet %s" % tweet['id'])
                    continue

                ids.add(tweet['id'])
                user = [user for user in users if user['id'] == tweet['author_id']][0]

                # some text cleanup
                text = re.sub(r'@\w+', '', tweet['text'])   # remove tagged users
                text = re.sub(r'[^\w.#:/\s]+', ' ', text)    # remove non word characters, except some
                text = text.replace('\n', ' ')              # remove linebreaks
                text = re.sub(r'\s{2,}', ' ', text)         # remove duplicate whitespaces
                text = text.casefold()                      # make the string lowercase

                data = {
                    'id': tweet['id'],
                    'tweet': text,
                    'author': tweet['author_id'],
                    'created_at': str(tweet['created_at']),
                    'engagements': sum(tweet['public_metrics'].values()),
                    'author_created_at': user['created_at'],
                    'verified': user['verified'],
                    'followers_count': user["public_metrics"]["followers_count"],
                    'friends_count': user["public_metrics"]["following_count"],
                    'statuses_count': user["public_metrics"]["tweet_count"],
                    'listedcount': user["public_metrics"]["listed_count"],
                    'author_location': user["location"] if "location" in user.keys() else "N/A"
                }

                producer.send(TOPIC_NAME, value=data)

            # avoid rate limits by the API
            time.sleep(2)

        logger.info("Scrape complete, waiting for %s hours" % (SLEEP_TIME / 60 / 60))
        logger.info("Currently at %s tweets" % len(ids))
        time.sleep(SLEEP_TIME)


if __name__ == '__main__':
    main()
