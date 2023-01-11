# label exported data from cassandra

import pickle
import pandas as pd

from consumer import clean


with open("model.pkl", "rb") as fp:
    model = pickle.load(fp)

df = pd.read_csv("~/BDMA/dashboard/data/twitter_labeled.csv")
df.drop(["label"], axis=1, inplace=True)

# clean the data, then apply the model
df["tweet"] = df["tweet"].apply(lambda x: clean(x))
df["label"] = df["tweet"].apply(lambda x: "fake" if model.predict([x])[0] == 0 else "real")

print(df["label"].value_counts())
df.to_csv("~/twitter_labeled.csv", index=False)
