import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor as GBRegressor, RandomForestRegressor

from persistence.model_storage import save_ml_model
from domain.data_preprocessor import prepare_data, split_X_y, prepare_X
from persistence.postgres.models import ModelType
import xgboost as xgb


def incremental_learning(train_data, test_data, ticker, model_type):
    train_data = prepare_data(train_data)
    train_data.to_csv("/tmp/train_data.csv", index=False)
    train_X, train_y = split_X_y(train_data)

    if model_type == ModelType.gradient_boosting:
        model = GBRegressor(
            n_estimators=300,
            learning_rate=0.05,
            max_depth=4,
            subsample=0.7,  # менее стабильные деревья
            max_features='sqrt',  # случайный поднабор признаков
        )
    elif model_type == ModelType.random_forest:
        model = RandomForestRegressor(
            n_estimators=100,
            max_depth=5,
            random_state=42
        )
    elif model_type == ModelType.xgboost:
        model = xgb.XGBRegressor(
            n_estimators=100,
            max_depth=4,
            learning_rate=0.1,
            use_label_encoder=False,
            eval_metric='logloss',
            random_state=42
        )

    model.fit(train_X, train_y)

    y_pred = []
    for index, row in test_data.iterrows():
        X = {
            'year': row['date'].year,
            'month': row['date'].month,
            'day': row['date'].day,
            # 'month_sin': np.sin(2 * np.pi * row['date'].month / 12),
            # 'month_cos': np.cos(2 * np.pi * row['date'].month / 12),
            # 'day_sin': np.sin(2 * np.pi * row['date'].day / 31),
            # 'day_cos': np.cos(2 * np.pi * row['date'].day / 31),
            'sma7': None,
            'sma30': None,
            'sma90': None,
            'sma180': None,
            'lag7': None,
            'lag45': None,
            'lag90': None,
            'lag180': None,
        }
        X = prepare_X(X, train_data)
        X = pd.DataFrame([X], index=[index])

        y = model.predict(X)[0]
        y_pred.append(y)
        X["close"] = y

        train_data = pd.concat([train_data, X], ignore_index=True)

    model_filename = save_ml_model(model, ticker)

    if model_type == ModelType.xgboost:
        # xgb uses numpy float32 which is not compatible with fastapi
        y_pred = [float(y) for y in y_pred]

    return y_pred, model_filename