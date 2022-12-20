import json
import logging

from kafka import KafkaConsumer, KafkaProducer


logging.basicConfig(
    format=(
        '%(asctime)s %(levelname)-8s[%(lineno)s: %(funcName)s] %(message)s'
    )
)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

TOPIC_NAME = 'twitter'
TWITTER_SINK_TOPIC = 'twittersink'
KAFKA_BROKER_URL = 'broker:9092'


def main():
    consumer = KafkaConsumer(
        TOPIC_NAME,
        bootstrap_servers=[KAFKA_BROKER_URL]
    )
    producer = KafkaProducer(
        bootstrap_servers=KAFKA_BROKER_URL,
        value_serializer=lambda x: json.dumps(x).encode('utf8'),
        api_version=(0, 10, 1)
    )

    for msg in consumer:
        data = json.loads(msg.value.decode('utf-8'))
        print(data)

        # do ML here

        logger.info("Sending data to topic %s" % TWITTER_SINK_TOPIC)
        producer.send(TWITTER_SINK_TOPIC, value=data)


if __name__ == '__main__':
    main()
