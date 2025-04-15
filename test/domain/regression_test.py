from datetime import datetime

import numpy as np
from dateutil.relativedelta import relativedelta

from persistence.clickhouse.stock_price_data_storage import get_min_max_dates, get_stock_data
from persistence.postgres.models import ModelType
from src.domain.regression import perform_experiment, create_model_from_experiment, perform_regression, get_next_business_day
from test.factories import create_test_researcher

def test_perform_experiment():
    researcher = create_test_researcher()

    experiment = perform_experiment(researcher, "T", "1983-11-21", "2018-03-01", "2018-03-02", "2018-04-02", ModelType.gradient_boosting)

def test_performing_regression():
    researcher = create_test_researcher()

    ticker = "T"
    train_from = "1983-11-21"
    train_to = "2018-03-01"
    train_test_from = (datetime.strptime(train_to, "%Y-%m-%d") + relativedelta(days=1)).strftime("%Y-%m-%d")
    train_test_to = (datetime.strptime(train_test_from, "%Y-%m-%d") + relativedelta(years=1)).strftime("%Y-%m-%d")
    test_from = get_next_business_day(train_test_to)
    test_to = (datetime.strptime(test_from, "%Y-%m-%d") + relativedelta(years=1)).strftime("%Y-%m-%d") # 1 year from test_from

    max_dates = get_min_max_dates(ticker)
    assert datetime.strptime(test_to, "%Y-%m-%d").date() < max_dates[1]

    print(f"\nExperiment: train from {train_from} to {train_to}, test from {train_test_from} to {train_test_to}")
    rmse, min, max, dates, y_test, y_pred, experiment = perform_experiment(researcher, ticker, train_from, train_to, train_test_from, train_test_to, ModelType.gradient_boosting)

    print(f"Creating model: from {train_from} to {train_test_to}")
    model = create_model_from_experiment(experiment)

    print(f"Performing regression: from {test_from} to {test_to}")
    dates, prices = perform_regression(model=model, date_from=test_from, date_to=test_to, ticker=None)
    assert len(dates) > 250

    test_values = get_stock_data(ticker, test_from, test_to)
    test_dates = [v[0].strftime('%Y-%m-%d') for v in test_values]
    assert abs(len(test_dates) - len(dates)) < 5, "Pred data len: " + str(len(dates)) + ", test data len: " + str(len(test_dates))
    test_prices = [v[4] for v in test_values]

    # Date lists are not equal since the US business calendar is not 100% precise
    matching_dates = set(dates) & set(test_dates)
    assert len(matching_dates) - len(dates) < 5
    filtered_test_prices = [test_prices[test_dates.index(date)] for date in matching_dates]
    filtered_prices = [prices[dates.index(date)] for date in matching_dates]
    assert len(filtered_test_prices) == len(filtered_prices)

    rmse = np.sqrt(np.mean((np.array(filtered_test_prices) - np.array(filtered_prices)) ** 2))
    print(f"RMSE: {rmse:.4f}, Min (Predicted): {np.min(prices):.2f}, Min (Actual): {np.min(test_prices):.2f}, "
          f"Max (Predicted): {np.max(prices):.2f}, Max (Actual): {np.max(test_prices):.2f}")