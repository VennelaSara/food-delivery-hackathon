import shap
import pandas as pd
from sklearn.ensemble import RandomForestRegressor

def train_explainable_model(df):
    features = df[[
        "rating"
    ]]
    target = df["total_amount"]

    model = RandomForestRegressor(
        n_estimators=100,
        random_state=42
    )
    model.fit(features, target)

    explainer = shap.Explainer(model, features)
    shap_values = explainer(features)

    return shap_values, features
