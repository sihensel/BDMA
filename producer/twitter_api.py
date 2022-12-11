import json
import logging
import re
import requests
import tweepy
from kafka import KafkaProducer

from keys import bearer_token, consumer_key, consumer_secret, access_token, access_token_secret


logging.basicConfig(
    format=(
        '%(asctime)s %(levelname)-8s[%(lineno)s: %(funcName)s] %(message)s'
    )
)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Kafka settings
TOPIC_NAME = 'twitter'
KAFKA_BROKER_URL = 'broker:9092'


def main():

    producer = KafkaProducer(
        bootstrap_servers=KAFKA_BROKER_URL,
        value_serializer=lambda x: json.dumps(x).encode('utf8'),
        api_version=(0, 10, 1)
    )

    client = tweepy.Client(
        bearer_token=bearer_token,
        consumer_key=consumer_key,
        consumer_secret=consumer_secret,
        access_token=access_token,
        access_token_secret=access_token_secret,
        return_type=requests.Response,
        wait_on_rate_limit=True
    )

    target_hashtags = {
        # '#Ukraine',
        '#UkraineWar',
        # '#UkraineNazis',
        # '#UkraineRussianWar',
        # '#RussianWarCrimes',
        # '#UkraineRussiaWar',
        # '#RussiaIsATerroristState'
    }

    logger.info("Getting Tweets from Twitter API")

    for tag in target_hashtags:
        logger.info("Scraping hashtag %s" % tag)
        response = client.search_recent_tweets(
            # FIXME recheck this search string
            '%s lang:en -is:retweet -is:quote -is:reply' % tag,
            tweet_fields=[
                'author_id',
                'created_at',
                'lang',
                'public_metrics'
            ],
            expansions=['author_id'],
            user_fields=['verified', 'location', 'created_at'],
            max_results=10
        ).json()

        tweets = response['data']
        users = response['includes']['users']

        for tweet in tweets:
            user = [user for user in users if user['id'] == tweet['author_id']][0]

            # remove tagged users from tweet
            text = re.sub(r'@\w+', '', tweet['text'])
            text = text.replace('\n', '')

            data = {
                'id': tweet['id'],
                'tweet': text,
                'author': tweet['author_id'],
                'created_at': str(tweet['created_at']),

                # FIXME this calculation is VERY basic
                'engagements': sum(tweet['public_metrics'].values()),

                'author_verified': user['verified'],
                'author_created_at': user['created_at'],

                # FIXME the location is often times set to some arbitrary location,
                # such as 'Moon' or 'Around', so maybe we should leave that out
                'author_location': user['location'] if 'location' in user.keys() else ''
            }

            logger.info("Sending data to topic %s" % TOPIC_NAME)
            producer.send(TOPIC_NAME, value=data)


if __name__ == '__main__':
    main()
