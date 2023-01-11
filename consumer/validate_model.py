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
        "favourites_count",
        "statuses_count",
        "verified"
    ]]
    label = df[["bot"]]

    prediction = clf.predict(attr)
    print_metrices(prediction, label)

    """
    Results:

    [[1146   30]
     [  46 1008]]
                  precision    recall  f1-score   support

               0       0.96      0.97      0.97      1176
               1       0.97      0.96      0.96      1054

        accuracy                           0.97      2230
       macro avg       0.97      0.97      0.97      2230
    weighted avg       0.97      0.97      0.97      2230

    Accuracy:	 0.9659192825112107
    Precison:	 0.966049385181528
    Recall:		 0.9659192825112107
    F1:		 0.9659344727436712
    """


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

    """ The model is really good at detecting fake tweets, but not at identifying real ones
    [[8389 1338]
     [ 405   69]]
                  precision    recall  f1-score   support

               0       0.95      0.86      0.91      9727
               1       0.05      0.15      0.07       474

        accuracy                           0.83     10201
       macro avg       0.50      0.50      0.49     10201
    weighted avg       0.91      0.83      0.87     10201

    Accuracy:	 0.8291343985883737
    Precison:	 0.7635678376562518
    Recall:		 0.8291343985883737
    F1:		 0.7910623380561452
    """


if __name__ == "__main__":
    validate_model()
    validate_bot_model()
