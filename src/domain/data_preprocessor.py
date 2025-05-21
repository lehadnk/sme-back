import numpy as np
import pandas as pd

def split_train_test(df, train_from: str, train_to: str, test_from: str, test_to):
    df['date'] = pd.to_datetime(df['date'])
    train = df[(df['date'] >= train_from) & (df['date'] <= train_to)].copy()
    test = df[(df['date'] >= test_from) & (df['date'] <= test_to)].copy()

    return train, test


def split_X_y(data):
    # if (data.get("year") is not None):
    X = data[
        [
            'year',
            'month',
            'day',
            'sma7',
            'sma30',
            'sma90',
            'sma180',
            'lag7',
            'lag45',
            'lag90',
            'lag180',
        ]
    ]
    # else:
    #     X = data['Date']

    y = data['close']

    return X, y


def prepare_data(data):
    data['year'] = data['date'].dt.year
    data['month'] = data['date'].dt.month
    data['day'] = data['date'].dt.day
    data['month'] = data['date'].dt.month.astype(str)
    # data['month_sin']: np.sin(2 * np.pi * data['date'].dt.month / 12)
    # data['month_cos']: np.cos(2 * np.pi * data['date'].dt.month / 12)
    # data['day_sin']: np.sin(2 * np.pi * data['date'].dt.day / 31)
    # data['day_cos']: np.cos(2 * np.pi * data['date'].dt.day / 31)

    data['sma7'] = data['close'].rolling(window=7).mean()
    data['sma30'] = data['close'].rolling(window=30).mean()
    data['sma90'] = data['close'].rolling(window=90).mean()
    data['sma180'] = data['close'].rolling(window=180).mean()

    data['lag7'] = data['sma30'].shift(7)
    data['lag45'] = data['sma30'].shift(45)
    data['lag90'] = data['sma30'].shift(90)
    data['lag180'] = data['sma30'].shift(180)

    data = data.dropna(subset=['lag180'])

    return data

def prepare_X(X, data):
    # @todo these values are a bit incorrect, since we don't use X['close'] to calculate smas
    X['sma7'] = data['close'].iloc[-7:].mean() if len(data) >= 7 else None
    X['sma30'] = data['close'].iloc[-30:].mean() if len(data) >= 30 else None
    X['sma90'] = data['close'].iloc[-90:].mean() if len(data) >= 90 else None
    X['sma180'] = data['close'].iloc[-180:].mean() if len(data) >= 180 else None

    X['lag180'] = data['sma30'].iloc[-180] if len(data) >= 180 else None
    X['lag90'] = data['sma30'].iloc[-90] if len(data) >= 90 else None
    X['lag45'] = data['sma30'].iloc[-45] if len(data) >= 45 else None
    X['lag7'] = data['sma30'].iloc[-7] if len(data) >= 7 else None

    return X