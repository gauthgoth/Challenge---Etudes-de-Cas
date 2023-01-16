import pandas as pd

def create_date_column(df):
    return pd.to_datetime(df['an'].astype(str)+'-'+df['mois'].astype(str)+'-'+df['jour'].astype(str))

def create_dow_column(df):
    return df['date'].dt.dayofweek