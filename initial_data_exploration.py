import pandas as pd

sales = pd.read_csv("data/raw/sales_train_validation.csv")
calendar = pd.read_csv("data/raw/calendar.csv")
prices = pd.read_csv("data/raw/sell_prices.csv")

print(sales.shape)
print(sales.head())
print(sales.isnull().sum())

print(calendar.shape)
print(calendar.head())
print(calendar.isnull().sum())

print(prices.shape)
print(prices.head())
print(prices.isnull().sum())