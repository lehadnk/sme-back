from persistence.clickhouse.stock_price_data_storage import get_stock_data
import pandas as pd

def load_stock_data(ticker: str, start_date: str, end_date: str):
    stock_data = get_stock_data(ticker, start_date, end_date)
    df = pd.DataFrame(stock_data, columns=['date', 'close'])
    df['date'] = pd.to_datetime(df['date'])

    return df
