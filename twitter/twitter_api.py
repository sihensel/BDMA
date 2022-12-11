import json
import requests
import tweepy
import logging
from kafka import KafkaProducer

from keys import *


logging.basicConfig(
    format=(
        '%(asctime)s %(levelname)-8s[%(lineno)s: %(funcName)s] %(message)s'
    )
)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Kafka settings
KAFKA_BROKER_URL = 'broker:9092'
TOPIC_NAME = 'twitter'
TWITTER_SINK_TOPIC = 'twittersink'


def main():

    client = tweepy.Client(
        bearer_token=bearer_token,
        consumer_key=consumer_key,
        consumer_secret=consumer_secret,
        access_token=access_token,
        access_token_secret=access_token_secret,
        return_type=requests.Response,
        wait_on_rate_limit=True
    )

    producer = KafkaProducer(
        bootstrap_servers=KAFKA_BROKER_URL,
        value_serializer=lambda x: json.dumps(x).encode('utf8'),
        api_version=(0, 10, 1)
    )

    logger.info("Getting Tweets from Twitter API")
    tweets = client.search_recent_tweets(
        query='from:BarackObama -is:retweet',
        tweet_fields=['author_id', 'created_at'],
        max_results=10
    )

    raw_data = tweets.json()['data']
    len_tweets = len(raw_data)
    logger.info("Found %s tweets" % len_tweets)

    for index, tweet in enumerate(raw_data):
        data = {
            'tweet': tweet['text'],
            'created_at': tweet['created_at'],
            'author': tweet['author_id']
        }

        logger.info("Sending data to topic %s (%s/%s)" %
                    (TOPIC_NAME, index + 1, len_tweets))
        producer.send(TOPIC_NAME, value=data)

        # also send the data to the sink
        logger.info("Sending data to topic %s (%s/%s)" %
                    (TWITTER_SINK_TOPIC, index + 1, len_tweets))
        producer.send(TWITTER_SINK_TOPIC, value=data)


if __name__ == '__main__':
    main()
