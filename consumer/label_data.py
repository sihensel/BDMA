# label exported data from cassandra

import pickle
import pandas as pd

from consumer import clean


with open("model.pkl", "rb") as fp:
    model = pickle.load(fp)

df = pd.read_csv("~/Downloads/exported/twitter.csv")
df.drop(["label"], axis=1, inplace=True)

# clean the data, then apply the model
df["tweet"] = df["tweet"].apply(lambda x: clean(x))
df["label"] = df["tweet"].apply(lambda x: "fake" if model.predict([x])[0] == 0 else "real")

df.rename(columns={"author_verified": "verified"}, inplace=True)
df["followers_count"] = 0
df["friends_count"] = 0
df["listedcount"] = 0
df["statuses_count"] = 0
df["author_location"] = "N/A"
df["bot"] = "N/A"

print(df["label"].value_counts())
df.to_csv("~/twitter_labeled.csv", index=False)
