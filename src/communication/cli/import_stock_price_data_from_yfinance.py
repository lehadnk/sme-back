from zoneinfo import ZoneInfo

import yfinance as yf
import pandas as pd
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from persistence.clickhouse.stock_price_data_storage import get_min_max_dates, insert_stock_data, \
    batch_insert_stock_data

if len(sys.argv) < 2:
    print("Please provide the ticker as a command-line argument.")
    sys.exit(1)

ticker = sys.argv[1]

min_date_str, max_date_str = get_min_max_dates(ticker)
data = yf.Ticker(ticker).history(period="max")
if len(data) == 0:
    print("No data to import")
    exit(0)

min_date = pd.to_datetime(min_date_str).replace(tzinfo=ZoneInfo("America/New_York"))
max_date = pd.to_datetime(max_date_str).replace(tzinfo=ZoneInfo("America/New_York"))

data.index = pd.to_datetime(data.index)
filtered_data = data[(data.index < min_date) | (data.index > max_date)]

data = []
for row in filtered_data.itertuples():
    date = row.Index.date()
    open_price = row.Open
    high = row.High
    low = row.Low
    close = row.Close
    print(close)

    adj_close = row.Close
    volume = row.Volume

    data.append((ticker, date, open_price, high, low, close, adj_close, volume))

batch_insert_stock_data(data)

if (len(filtered_data) == 0):
    print("No additional data to import")
    exit(0)

min_filtered_date = filtered_data.index.min().date().isoformat()
max_filtered_date = filtered_data.index.max().date().isoformat()

print(f"Successfully imported {ticker} data from yfinance: " + str(len(data)) + " rows was imported. For the period of " + min_filtered_date + " to " + max_filtered_date)