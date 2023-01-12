import pickle
import pandas as pd
from sklearn import tree
from sklearn.model_selection import train_test_split

from train_model import print_metrices


def train_bot_model():
    # labeled data from:
    # https://github.com/RohanBhirangi/Twitter-Bot-Detection/blob/master/kaggle_train.csv
    df = pd.read_csv("/home/simon/Downloads/data/bot_train.csv")

    X = df[[
        'followers_count',      # users that are following the user
        'friends_count',        # users the user is following
        'listedcount',          # number of lists that the user is a member of
        # 'favourites_count',     # amount of tweets the user liked -> removed from Twitter API
        'statuses_count',       # amount of tweets the users created
        'verified'              # whether the user is verified
    ]]
    Y = df[['bot']]

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        Y,
        test_size=0.2,
        shuffle=True,
        random_state=42
    )

    clf = tree.DecisionTreeClassifier()
    clf.fit(X_train, y_train)
    prediction = clf.predict(X_test)

    print_metrices(prediction, y_test)

    with open("model_bot.pkl", "wb") as fp:
        pickle.dump(clf, fp)


if __name__ == "__main__":
    train_bot_model()