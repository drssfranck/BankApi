import pandas as pd

PKL_PATH = "data.pkl"

def load_dataset():
    return pd.read_pickle(PKL_PATH)