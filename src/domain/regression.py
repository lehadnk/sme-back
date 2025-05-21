import math
from datetime import datetime, timedelta
from typing import Optional

import numpy as np
import pandas as pd
from dateutil.relativedelta import relativedelta

from sklearn.ensemble import GradientBoostingRegressor
from sklearn.metrics import mean_squared_error

from persistence.clickhouse.stock_price_data_storage import get_min_max_dates, insert_prediction
from persistence.postgres.db import save_experiment, save_model, get_best_model_for_date_and_ticker
from persistence.postgres.models import Experiment, Model, User
from persistence.model_storage import save_ml_model, load_ml_model
from domain.data_preprocessor import prepare_data, split_train_test, split_X_y, prepare_X
from domain.learning import incremental_learning
from domain.stock_data_loader import load_stock_data
from pandas.tseries.holiday import USFederalHolidayCalendar


def calculate_rmse(y_pred, y_test) -> [float, float, float]:
    rmse = math.sqrt(mean_squared_error(y_pred, y_test))
    return rmse, y_test.min(), y_test.max()

def perform_experiment(author: User, ticker: str, train_from: str, train_to: str, test_from: str, test_to: str, model_type: str):
    stock_data = load_stock_data(ticker, train_from, test_to)
    train, test = split_train_test(stock_data, train_from, train_to, test_from, test_to)
    y_pred, model_filename = incremental_learning(train, test, ticker, model_type)

    y_test = test['close']
    rmse, min, max = calculate_rmse(y_pred, y_test)

    experiment = Experiment(
        author_id=author.id,
        train_data_from=datetime.strptime(train_from, "%Y-%m-%d"),
        train_data_to=datetime.strptime(train_to, "%Y-%m-%d"),
        test_data_from=datetime.strptime(test_from, "%Y-%m-%d"),
        test_data_to=datetime.strptime(test_to, "%Y-%m-%d"),
        ticker=ticker,
        rmse=float(rmse),
        min=float(min),
        max=float(max),
        regression_model=model_type,
        model_filename=model_filename,
    )
    save_experiment(experiment)

    return rmse, min, max, test['date'], y_test, y_pred, experiment

def perform_regression(model: Optional[Model], ticker: Optional[str], date_from: str, date_to: str):
    if model is None and ticker is None:
        raise Exception("You must specify a model or a ticker")

    date_from_obj = datetime.strptime(date_from, '%Y-%m-%d')
    date_from_minus_one_year = date_from_obj - relativedelta(years=1)

    if model is None:
        model = get_best_model_for_date_and_ticker(ticker, date_from_minus_one_year.strftime('%Y-%m-%d'))

    if model is None:
        raise Exception("No model was found for ticker " + ticker)

    historical_data_from = (model.train_data_to - relativedelta(days=580)).strftime('%Y-%m-%d') # todo business days
    historical_data_to = model.train_data_to.strftime('%Y-%m-%d')

    stock_data = load_stock_data(model.ticker, historical_data_from, historical_data_to)
    stock_data = prepare_data(stock_data)

    ml_model = load_ml_model(model.model_filename)

    dates = []
    close_values = []

    current_date = get_next_business_day(historical_data_to)
    while current_date <= date_to:
        X = {
            'year': datetime.strptime(current_date, '%Y-%m-%d').year,
            'month': datetime.strptime(current_date, '%Y-%m-%d').month,
            'day': datetime.strptime(current_date, '%Y-%m-%d').day,
            # 'month_sin': np.sin(2 * np.pi * datetime.strptime(current_date, '%Y-%m-%d').month / 12),
            # 'month_cos': np.cos(2 * np.pi * datetime.strptime(current_date, '%Y-%m-%d').month / 12),
            # 'day_sin': np.sin(2 * np.pi * datetime.strptime(current_date, '%Y-%m-%d').day / 31),
            # 'day_cos': np.cos(2 * np.pi * datetime.strptime(current_date, '%Y-%m-%d').day / 31),
            'sma7': None,
            'sma30': None,
            'sma90': None,
            'sma180': None,
            'lag7': None,
            'lag45': None,
            'lag90': None,
            'lag180': None,
        }
        prepare_X(X, stock_data)
        X_df = pd.DataFrame([X])
        X['close'] = ml_model.predict(X_df)[0]

        if current_date >= date_from:
            dates.append(current_date)
            close_values.append(X['close'])

        current_date = get_next_business_day(current_date)

    return dates, close_values


def get_next_business_day(date_str: str) -> str:
    date = datetime.strptime(date_str, '%Y-%m-%d')
    us_bdays = pd.tseries.offsets.CustomBusinessDay(
        holidays=USFederalHolidayCalendar().holidays()
    )

    next_business_day = date + us_bdays

    return next_business_day.strftime('%Y-%m-%d')

def create_model_from_experiment(experiment: Experiment):
    stock_data = load_stock_data(experiment.ticker, experiment.train_data_from.strftime("%Y-%m-%d"), experiment.test_data_to.strftime("%Y-%m-%d"))
    stock_data = prepare_data(stock_data)
    X_train, y_train = split_X_y(stock_data)

    model = GradientBoostingRegressor(n_estimators=100, learning_rate=0.1, max_depth=3)
    model.fit(X_train, y_train)
    save_ml_model(model, experiment.ticker)

    model = Model(
        author_id=experiment.author_id,
        train_data_from=experiment.train_data_from,
        train_data_to=experiment.train_data_to,
        ticker=experiment.ticker,
        rmse=experiment.rmse,
        min=experiment.min,
        max=experiment.max,
        regression_model=experiment.regression_model,
        model_filename=experiment.model_filename,
    )
    save_model(model)

    min_max_dates = get_min_max_dates(experiment.ticker)
    date_obj = min_max_dates[1]
    next_day = date_obj + timedelta(days=1)
    six_months_later = date_obj + relativedelta(days=35)
    next_day_str = next_day.strftime("%Y-%m-%d")
    six_months_later_str = six_months_later.strftime("%Y-%m-%d")
    print("Calculating predictions from " + next_day_str + " to " + six_months_later_str + " for " + experiment.ticker)

    dates, predictions = perform_regression(model, None, next_day_str, six_months_later_str)

    for date, prediction in zip(dates, predictions):
        insert_prediction(model.ticker, date, datetime.today().strftime("%Y-%m-%d"), model.id, prediction)

    return model

def train_model(X_train, y_train, X_test, ticker):
    model = GradientBoostingRegressor(n_estimators=100, learning_rate=0.1, max_depth=3)
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    model_filename = save_ml_model(model, ticker)
    return y_pred, model_filename
