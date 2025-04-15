import csv
import os
import sys
from datetime import datetime

from clickhouse_driver import Client

if len(sys.argv) < 2:
    print("Please provide the directory path as a command-line argument.")
    sys.exit(1)

directory = sys.argv[1]
if not os.path.isdir(directory):
    print(f"The specified directory '{directory}' does not exist.")
    sys.exit(1)

filter = None if len(sys.argv) < 3 else sys.argv[2]

client = Client(
    host="localhost",
    port=9000,
    user="default",
    password="qwe",
    database="default",
)

def safe_float(value):
    try:
        return float(value) if value else 0.0
    except ValueError:
        return 0.0

def insert_data_from_csv(file_path, ticker):
    if (filter is not None and ticker != filter):
        return

    print(f"Importing {ticker} data from {file_path}...")

    with open(file_path, 'r') as f:
        csv_reader = csv.reader(f)
        next(csv_reader) # Skip the header row

        data = []
        batch_size = 100  # Set a batch size for the inserts
        for row in csv_reader:
            date = datetime.strptime(row[0], '%Y-%m-%d').date()
            open_price = safe_float(row[1])
            high = safe_float(row[2])
            low = safe_float(row[3])
            close = safe_float(row[4])
            adj_close = safe_float(row[5])
            volume = int(float(row[6])) if row[6] else 0

            data.append((ticker, date, open_price, high, low, close, adj_close, volume))

            if len(data) >= batch_size:
                client.execute('INSERT INTO stock_data (ticker, date, open, high, low, close, adj_close, volume) VALUES', data)
                data = []

        if data:
            client.execute('INSERT INTO stock_data (ticker, date, open, high, low, close, adj_close, volume) VALUES', data)

    print(f"Successfully imported {ticker} data from {file_path}.")


for filename in os.listdir(directory):
    if filename.endswith('.csv'):
        ticker = os.path.splitext(filename)[0]
        file_path = os.path.join(directory, filename)

        insert_data_from_csv(file_path, ticker)