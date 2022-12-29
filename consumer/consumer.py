import json
import logging
import pickle
import re
import nltk
from nltk.corpus import stopwords
from kafka import KafkaConsumer, KafkaProducer


logging.basicConfig(
    format=(
        "%(asctime)s %(levelname)-8s[%(lineno)s: %(funcName)s] %(message)s"
    )
)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

TOPIC_NAME = "twitter"
TWITTER_SINK_TOPIC = "twittersink"
KAFKA_BROKER_URL = "broker:9092"


def clean(string):
    """ Clean the provided string """
    stop = stopwords.words("english")

    text = string.lower().split()
    text = " ".join(text)
    text = re.sub(r"http(\S)+", " ", text)
    text = re.sub(r"www(\S)+", " ", text)
    text = re.sub(r"&", " and ", text)
    text = re.sub(r"[^#0-9a-zA-Z]+", " ", text)
    text = re.sub(r"\s{2,}", " ", text)
    text = text.split()
    text = [w for w in text if w not in stop]
    text = " ".join(text)
    return text


def main():
    consumer = KafkaConsumer(
        TOPIC_NAME,
        bootstrap_servers=[KAFKA_BROKER_URL]
    )
    producer = KafkaProducer(
        bootstrap_servers=KAFKA_BROKER_URL,
        value_serializer=lambda x: json.dumps(x).encode("utf8"),
        api_version=(0, 10, 1)
    )

    with open("model.pkl", "rb") as fp:
        model = pickle.load(fp)

    for msg in consumer:
        data = json.loads(msg.value.decode("utf-8"))

        tweet = clean(data["tweet"])
        result = model.predict([tweet])[0]

        # 0 = fake; 1 = real
        if result == 0:
            data["label"] = "fake"
        elif result == 1:
            data["label"] = "real"

        data["tweet"] = tweet

        producer.send(TWITTER_SINK_TOPIC, value=data)


if __name__ == "__main__":
    nltk.download("stopwords")

    main()
