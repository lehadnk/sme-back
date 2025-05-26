import csv
import os
from datetime import datetime
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from persistence.clickhouse.stock_price_data_storage import insert_stock_data

if len(sys.argv) < 2:
    print("Please provide the directory path as a command-line argument.")
    sys.exit(1)

directory = sys.argv[1]
if not os.path.isdir(directory):
    print(f"The specified directory '{directory}' does not exist.")
    sys.exit(1)

filter = None if len(sys.argv) < 3 else sys.argv[2]

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
        batch_size = 1000  # Set a batch size for the inserts
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
                insert_stock_data(data)
                data = []

        if data:
            insert_stock_data(data)

    print(f"Successfully imported {ticker} data from {file_path}.")


for filename in os.listdir(directory):
    if filename.endswith('.csv'):
        ticker = os.path.splitext(filename)[0]
        file_path = os.path.join(directory, filename)

        insert_data_from_csv(file_path, ticker)