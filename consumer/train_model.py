import pickle
import re

import nltk
from nltk.corpus import stopwords

import pandas as pd

from sklearn import tree
from sklearn.utils import shuffle
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score, recall_score, precision_score
from sklearn.metrics import f1_score, classification_report, confusion_matrix
from sklearn.model_selection import train_test_split


def clean(string):
    """ Clean the provided string """
    stop = stopwords.words("english")

    text = string.lower().split()
    text = " ".join(text)
    text = re.sub(r"http(\S)+", " ", text)
    text = re.sub(r"www(\S)+", " ", text)
    text = re.sub(r"&", " and ", text)
    text = re.sub(r"[^0-9a-zA-Z]+", " ", text)
    text = text.split()
    text = [w for w in text if w not in stop]
    text = [w for w in text if not w.startswith('#')]
    text = " ".join(text)
    return text


def print_metrices(pred, true):
    """ Print evaluation metrics of a trained and tested model """
    print(confusion_matrix(true, pred))
    print(classification_report(true, pred))
    print("Accuracy:\t", accuracy_score(pred, true))
    print("Precison:\t", precision_score(pred, true, average="weighted"))
    print("Recall:\t\t", recall_score(pred, true, average="weighted"))
    print("F1:\t\t", f1_score(pred, true, average="weighted"))


def train_model():
    # labeled data from https://www.kaggle.com/datasets/saurabhshahane/fake-news-classification
    # import data
    df = pd.read_csv("~/Downloads/WELFake_Dataset.csv")
    # df["text"] = df["text"].astype(str)
    df["title"] = df["title"].astype(str)
    # df.drop(["title"], axis=1, inplace=True)

    # clean data
    df["title"] = df["title"].map(lambda x: clean(x))

    df = shuffle(df)
    df = df.reset_index(drop=True)

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
        ("classifier", tree.DecisionTreeClassifier())
    ])

    pipe.fit(X_train, y_train)
    prediction = pipe.predict(X_test)

    print_metrices(prediction, y_test)

    # export trained model
    with open("model.pkl", "wb") as fp:
        pickle.dump(pipe, fp)


if __name__ == "__main__":
    nltk.download("stopwords")

    train_model()
