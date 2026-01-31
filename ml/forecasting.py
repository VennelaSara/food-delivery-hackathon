import pandas as pd
from prophet import Prophet

def prepare_forecast_data(df):
    daily = (
        df.groupby("order_date")["total_amount"]
        .sum()
        .reset_index()
        .rename(columns={
            "order_date": "ds",
            "total_amount": "y"
        })
    )
    return daily

def run_forecast(df, periods=30):
    prophet_df = prepare_forecast_data(df)

    model = Prophet(
        yearly_seasonality=True,
        weekly_seasonality=True,
        daily_seasonality=False
    )

    model.fit(prophet_df)

    future = model.make_future_dataframe(periods=periods)
    forecast = model.predict(future)

    return forecast, model
