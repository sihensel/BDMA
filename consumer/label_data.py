# label exported data from cassandra in retrospect

import pickle
import pandas as pd

from consumer import clean


with open("model.pkl", "rb") as fp:
    model = pickle.load(fp)

df = pd.read_csv("~/twitter_unlabeled.csv")

# clean the data, then apply the model
df["tweet"] = df["tweet"].apply(lambda x: clean(x))
df["label"] = df["tweet"].apply(lambda x: "fake" if model.predict([x])[0] == 0 else "real")

df.to_csv("~/twitter_labeled.csv", index=False)
