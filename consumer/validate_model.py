import pickle
import pandas as pd

from train_model import print_metrices


def validate_bot_model():

    with open("model_bot.pkl", "rb") as fp:
        clf = pickle.load(fp)

    # verification data from:
    # https://github.com/RohanBhirangi/Twitter-Bot-Detection/blob/master/bots_data.csv
    # https://github.com/RohanBhirangi/Twitter-Bot-Detection/blob/master/nonbots_data.csv
    bots = pd.read_csv("~/Downloads/bots_clean.csv")
    nonbots = pd.read_csv("~/Downloads/non_bots_clean.csv")

    df = pd.concat([bots, nonbots])

    attr = df[[
        'followers_count',
        'friends_count',
        'listedcount',
        'favourites_count',
        'statuses_count',
        'verified'
    ]]
    label = df[['bot']]

    predicted = clf.predict(attr)
    print_metrices(predicted, label)

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


if __name__ == '__main__':
    validate_bot_model()
