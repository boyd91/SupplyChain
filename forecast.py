import pandas as pd
import sqlite3

def load_data():
    conn = sqlite3.connect("data/db/supply_chain.db")
    df = pd.read_sql("SELECT * FROM demand WHERE date >= '2015-01-01'", conn)
    conn.close()
    return df


def prepare_time_series(df):
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values(['item_id', 'store_id', 'date'])

    # lag feature
    df['lag_7'] = df.groupby(['item_id','store_id'])['sales'].shift(7)
    df['rolling_mean_7'] = df.groupby(['item_id','store_id'])['sales'].transform(lambda x: x.rolling(7).mean())

    return df


def simple_forecast(df):
    # ใช้ rolling mean เป็น forecast
    forecast = df.groupby(['item_id','store_id'])['rolling_mean_7'].last().reset_index()
    forecast.rename(columns={'rolling_mean_7': 'forecast'}, inplace=True)
    return forecast


if __name__ == "__main__":
    df = load_data()
    df = prepare_time_series(df)
    fc = simple_forecast(df)

    print(fc.head())

conn = sqlite3.connect("data/db/supply_chain.db")
fc.to_sql("forecast", conn, if_exists="replace", index=False)
conn.close()