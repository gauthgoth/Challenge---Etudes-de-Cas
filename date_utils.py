import pandas as pd

def create_date_column(df):
    return pd.to_datetime(df['an'].astype(str)+'-'+df['mois'].astype(str)+'-'+df['jour'].astype(str))

def create_dow_column(df):
    return df['date'].dt.dayofweek

def add_day_month_year(df):
    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.month
    df['day'] = df['date'].dt.day
    df['day_of_week'] = df['date'].dt.weekday

def add_holidays(df,df_holidays):
    df['is_holiday'] = 0
    df.loc[df.date.isin(df_holidays.date) , 'is_holiday'] = 1