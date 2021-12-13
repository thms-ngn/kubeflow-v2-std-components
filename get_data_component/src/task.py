import pandas as pd
from sklearn import datasets
from sklearn.model_selection import train_test_split as tts
from kfp.v2.dsl import *


def ingest() -> (pd.DataFrame, pd.DataFrame):
    # import some data to play with

    data_raw = datasets.load_breast_cancer()
    data = pd.DataFrame(data_raw.data, columns=data_raw.feature_names)
    data["target"] = data_raw.target

    train, test = tts(data, test_size=0.3)

    return train, test


def ingest_comp(
        train_path: Output[Dataset],
):
    train_path = Dataset(uri=train_path)
    print('TRAIN PATH: ' + train_path.uri)
    train_df, test_df = ingest()
    train_path.metadata['foo2'] = 'bar'

    # train_df.to_csv(train_path.path) # will not work
    train_df.to_csv(train_path.uri)
