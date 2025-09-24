import pandas as pd

df = pd.read_csv('data/app_data.csv', index_col=0, header=0)

def get_value (key):
    value = df.loc[key].iloc[0]
    return value