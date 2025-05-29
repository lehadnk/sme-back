from fastapi import APIRouter, Query

from persistence.clickhouse.stock_price_data_storage import get_stock_data, get_unique_tickers, get_min_max_dates, \
    get_most_growing_stocks

stocks_router = APIRouter()

@stocks_router.get("/stocks/prices")
def get_stock_price_date(
    ticker: str = Query(..., description="The stock ticker symbol."),
    start_date: str = Query(..., description="The start date in YYYY-MM-DD format."),
    end_date: str = Query(..., description="The end date in YYYY-MM-DD format."),
):
    print("In: get_stock_price_date")

    result = get_stock_data(ticker, start_date, end_date)

    dates = [row[0] for row in result]  # First column is the date
    closing_prices = [row[1] for row in result]  # Fifth column is the closing price

    return {"dates": dates, "closing_prices": closing_prices}

@stocks_router.get("/stocks/tickers")
def get_tickers():
    print("In: get_tickers")

    return get_unique_tickers()

@stocks_router.get("/stocks/tickers/{ticker}")
def get_ticker_min_max_dates(ticker: str):
    print("In: get_ticker_min_max_dates")

    dates = get_min_max_dates(ticker)
    return {"from": dates[0], "to": dates[1]}

@stocks_router.get("/stocks/most-growing")
def get_most_growing(comparison_date: str, forecast_date: str):
    print("In: get_most_growing")

    return get_most_growing_stocks(comparison_date, forecast_date)