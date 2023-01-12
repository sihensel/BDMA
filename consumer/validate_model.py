import pickle
import pandas as pd

from consumer import clean
from train_model import print_metrices


def validate_bot_model():
    print("Validating Twitter bot detection model...")

    with open("model_bot.pkl", "rb") as fp:
        clf = pickle.load(fp)

    # verification data from:
    # https://github.com/RohanBhirangi/Twitter-Bot-Detection/blob/master/bots_data.csv
    # https://github.com/RohanBhirangi/Twitter-Bot-Detection/blob/master/nonbots_data.csv
    bots = pd.read_csv("~/Downloads/data/bot_validate.csv")
    nonbots = pd.read_csv("~/Downloads/data/nonbot_validate.csv")

    df = pd.concat([bots, nonbots])

    attr = df[[
        "followers_count",
        "friends_count",
        "listedcount",
        # "favourites_count",
        "statuses_count",
        "verified"
    ]]
    label = df[["bot"]]

    prediction = clf.predict(attr)
    print_metrices(prediction, label)


def validate_model():
    print("Validating fake tweet detection model...")

    with open("model.pkl", "rb") as fp:
        pipe = pickle.load(fp)

    # validate with dataset containing fake tweets
    # from: https://zenodo.org/record/4282522#.Yt6cGXZBy3A
    df = pd.read_csv("~/Downloads/data/validate_twitter.csv")
    df["title"] = df["title"].map(lambda x: clean(str(x)))

    attr = df["title"]
    label = df["label"]

    prediction = pipe.predict(attr)
    print_metrices(prediction, label)


if __name__ == "__main__":
    validate_model()
    validate_bot_model()
