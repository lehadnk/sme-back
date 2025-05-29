from collections import defaultdict
from datetime import datetime

from config import pool


def import_data():
    pass

def get_stock_data(ticker: str, start_date: str, end_date: str):
    print("In: get_stock_data")

    with pool.get_client() as ch_client:
        query = """
            SELECT date, close
            FROM stock_data
            WHERE ticker = %(ticker)s AND date BETWEEN %(start_date)s AND %(end_date)s
            ORDER BY date
        """

        result = ch_client.query(query, parameters={"ticker": ticker, "start_date": start_date, "end_date": end_date}).result_rows
        return result

def get_unique_tickers():
    print("In: get_unique_tickers)")

    with pool.get_client() as ch_client:
        query = """
            SELECT DISTINCT ticker
            FROM stock_data
            ORDER BY ticker
            """

        result = ch_client.query(query).result_rows
        return [row[0] for row in result]

def get_min_max_dates(ticker: str):
    print("In: get_min_max_dates")

    with pool.get_client() as ch_client:
        query = """
            SELECT MIN(date) AS min_date, MAX(date) AS max_date
            FROM stock_data
            WHERE ticker = %(ticker)s
    
        """

        result = ch_client.query(query, parameters={"ticker": ticker}).result_rows
        return result[0]

def get_most_growing_stocks(comparison_date, forecast_date):
    print("In: get_most_growing_stocks")

    with pool.get_client() as ch_client:
        query = """
            SELECT ticker, (p.close / sd.close) - 1 as growth, sd.close, p.close
            FROM stock_data sd
            JOIN (
                SELECT ticker, close
                FROM (
                    SELECT ticker, close, ROW_NUMBER() OVER (PARTITION BY ticker, date ORDER BY estimated_at DESC) AS rn
                    FROM predictions
                    WHERE date = %(forecast_date)s
                ) ranked
                WHERE rn = 1
            ) p ON sd.ticker = p.ticker
            WHERE date = %(comparison_date)s
            ORDER BY growth DESC
        """

        result = ch_client.query(query, parameters={"comparison_date": comparison_date, "forecast_date": forecast_date}).result_rows
        return [{"ticker": row[0], "growth": row[1], "today_close": row[2], "forecast_close": row[3]} for row in result]

def insert_predictions(predictions: list):
    print("In: insert_predictions")

    with pool.get_client() as ch_client:
        ch_client.insert(
            'predictions',
            predictions,
            ['ticker', 'date', 'estimated_at', 'model_id', 'close']
        )


def batch_insert_stock_data(data, batch_partition_limit=100):
    print("In: batch_insert_stock_data")

    partitions = defaultdict(list)
    for row in data:
        dt = row[1]
        partition_key = dt.year * 100 + dt.month  # toYYYYMM equivalent
        partitions[partition_key].append(row)

    partition_keys = list(partitions.keys())
    for i in range(0, len(partition_keys), batch_partition_limit):
        batch_keys = partition_keys[i:i+batch_partition_limit]
        batch_data = []
        for key in batch_keys:
            batch_data.extend(partitions[key])
        insert_stock_data(batch_data)

def insert_stock_data(data: list):
    print("In: insert_stock_data")

    with pool.get_client() as ch_client:
        ch_client.insert(
            'stock_data',
            data,
            ['ticker', 'date', 'open', 'high', 'low', 'close', 'adj_close', 'volume']
        )