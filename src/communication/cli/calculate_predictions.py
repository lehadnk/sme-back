import datetime
import sys

from persistence.postgres.db import get_best_models_for_tickers_with_train_data_to_at_least
from persistence.clickhouse.stock_price_data_storage import insert_prediction
from domain.regression import perform_regression

if len(sys.argv) < 3:
    print("Требуемые параметры: <дата: от> <дата: до>")
    exit(1)

date_from = sys.argv[1]
date_to = sys.argv[2]

filter = None if len(sys.argv) < 4 else sys.argv[3]

print("Расчет выполняется с " + date_from + " по " + date_to)

min_train_data_to = '2020-03-01'

best_models = get_best_models_for_tickers_with_train_data_to_at_least(min_train_data_to)

for model in best_models:
    if filter and model.ticker != filter:
        continue

    print("Расчет предсказаний для " + model.ticker + "...")
    dates, predictions = perform_regression(model, None, date_from, date_to)

    for date, prediction in zip(dates, predictions):
        insert_prediction(model.ticker, date, datetime.date.today().strftime("%Y-%m-%d"), model.id, prediction)

    print("Расчет предсказаний для " + model.ticker + " закончен.")