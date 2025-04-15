import os
import pickle
from datetime import datetime

from config import EXPERIMENT_MODELS_DIR


def save_ml_model(model, ticker: str):
    if not os.path.exists(EXPERIMENT_MODELS_DIR):
        os.makedirs(EXPERIMENT_MODELS_DIR)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"{ticker}_{timestamp}.pkl"
    file_path = os.path.join(EXPERIMENT_MODELS_DIR, filename)

    with open(file_path, 'wb') as f:
        pickle.dump(model, f)

    return file_path

def load_ml_model(file_path: str):
    with open(file_path, 'rb') as f:
        model = pickle.load(f)

    return model