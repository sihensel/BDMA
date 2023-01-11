import pickle
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score, recall_score, precision_score
from sklearn.metrics import f1_score, classification_report, confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.linear_model import PassiveAggressiveClassifier

from consumer import clean


def print_metrices(pred, true):
    """ Print evaluation metrics of a trained and tested model """
    print(confusion_matrix(true, pred))
    print(classification_report(true, pred))
    print("Accuracy:\t", accuracy_score(pred, true))
    print("Precison:\t", precision_score(pred, true, average="weighted"))
    print("Recall:\t\t", recall_score(pred, true, average="weighted"))
    print("F1:\t\t", f1_score(pred, true, average="weighted"))


def train_model():
    # labeled data from:
    # https://github.com/Sairamvinay/Fake-News-Dataset/blob/master/fake-news/train_clean.csv
    df = pd.read_csv("~/Downloads/data/train_twitter.csv")

    # train on news article titles, as they come closer to tweets
    df["title"] = df["title"].astype(str)

    # clean data
    df["title"] = df["title"].map(lambda x: clean(x))

    # invert labels: 0 = fake; 1 = real
    df["label"] = df["label"].map({1: 0, 0: 1})

    # split the data
    X_train, X_test, y_train, y_test = train_test_split(
        df["title"],
        df["label"],
        test_size=0.2,
        random_state=42
    )

    # create and train the model
    pipe = Pipeline([
        ("bow", CountVectorizer()),
        ("tfidf", TfidfTransformer()),
        ("classifier", PassiveAggressiveClassifier(max_iter=50))
    ])

    pipe.fit(X_train, y_train)
    prediction = pipe.predict(X_test)

    print_metrices(prediction, y_test)

    # # export trained model
    with open("model.pkl", "wb") as fp:
        pickle.dump(pipe, fp)


if __name__ == "__main__":
    train_model()
