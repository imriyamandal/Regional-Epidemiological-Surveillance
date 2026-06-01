"""Time series models: Prophet, ARIMA, SARIMA."""

from __future__ import annotations

import pandas as pd


def fit_prophet(series: pd.DataFrame, date_col: str = "report_date", value_col: str = "case_count"):
    from prophet import Prophet

    df = series[[date_col, value_col]].rename(columns={date_col: "ds", value_col: "y"})
    model = Prophet(yearly_seasonality=True, weekly_seasonality=False, daily_seasonality=False)
    model.fit(df)
    future = model.make_future_dataframe(periods=6, freq="MS")
    forecast = model.predict(future)
    return model, forecast


def fit_sarima(series: pd.Series, order: tuple = (1, 1, 1), seasonal_order: tuple = (1, 1, 1, 12)):
    from statsmodels.tsa.statespace.sarimax import SARIMAX

    model = SARIMAX(series, order=order, seasonal_order=seasonal_order)
    fitted = model.fit(disp=False)
    forecast = fitted.forecast(steps=6)
    return fitted, forecast


def fit_arima(series: pd.Series, order: tuple = (2, 1, 2)):
    from statsmodels.tsa.arima.model import ARIMA

    model = ARIMA(series, order=order)
    fitted = model.fit()
    forecast = fitted.forecast(steps=6)
    return fitted, forecast
