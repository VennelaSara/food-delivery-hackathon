import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans

def build_user_features(df):
    user_df = (
        df.groupby("user_id")
        .agg(
            total_orders=("order_id", "count"),
            total_spent=("total_amount", "sum"),
            avg_order_value=("total_amount", "mean"),
            avg_rating=("rating", "mean")
        )
        .reset_index()
    )
    return user_df

def segment_users(df, n_clusters=4):
    user_df = build_user_features(df)

    features = user_df[[
        "total_orders",
        "total_spent",
        "avg_order_value",
        "avg_rating"
    ]]

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(features)

    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    user_df["segment"] = kmeans.fit_predict(X_scaled)

    return user_df
