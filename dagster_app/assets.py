import pickle

import numpy as np
import pandas as pd
from dagster import (
    Config,
    MaterializeResult,
    MetadataValue,
    asset,
)
from enerfore.forecasting.ts.recipes.load import LoadGbrtARX


class DataConfig(Config):
    y_train_path: str = "dagster_app/data/y_train.csv"
    x_train_path: str = "dagster_app/data/x_train.csv"
    x_pred_path: str = "dagster_app/data/x_pred.csv"
    model_train_path: str = "dagster_app/data/model_train.pkl"
    y_pred_path: str = "dagster_app/data/y_pred.csv"


@asset
def y_train(config: DataConfig):
    index = pd.date_range(start="2024-01-01", end="2024-12-31", freq="H")
    data = np.sin((index.hour / 24) * 2 * np.pi) + np.random.normal(0, 0.1, len(index))
    df = pd.DataFrame(data, index=index, columns=["y"])
    df.to_csv(config.y_train_path)


@asset
def x_train(config: DataConfig):
    index = pd.date_range(start="2024-01-01", end="2024-12-31", freq="H")
    data = np.cos((index.hour / 24) * 2 * np.pi) * 1.5 + np.random.normal(0, 0.2, len(index))
    df = pd.DataFrame(data, index=index, columns=["X"])
    df.to_csv(config.x_train_path)


@asset
def x_pred(config: DataConfig):
    index = pd.date_range(start="2025-01-01", end="2025-02-28", freq="H")
    data = np.cos((index.hour / 24) * 2 * np.pi) * 1.5 + np.random.normal(0, 0.2, len(index))
    df = pd.DataFrame(data, index=index, columns=["X"])
    df.to_csv(config.x_pred_path)


@asset(deps=[y_train, x_train])
def model_train(config: DataConfig):
    y_train = pd.read_csv(config.y_train_path, index_col=0, parse_dates=True)
    x_train = pd.read_csv(config.x_train_path, index_col=0, parse_dates=True)
    model = LoadGbrtARX(freq="1H")
    model.fit(y_train, x_train)
    pickle.dump(model, open(config.model_train_path, "wb"))


@asset(deps=[x_pred, model_train])
def model_predict(config: DataConfig) -> MaterializeResult:
    x_pred = pd.read_csv(config.x_pred_path, index_col=0, parse_dates=True)
    model_train = pickle.load(open(config.model_train_path, "rb"))
    fh = pd.date_range(start="2025-01-01", end="2025-02-28", freq="H")
    y_pred = model_train.predict(X=x_pred, fh=fh)
    y_pred.to_csv(config.y_pred_path)
    return MaterializeResult(
        metadata={
            "num_records": len(y_pred),
            "preview": MetadataValue.md(str(y_pred.head())),
        }
    )
