"""
Builds the final analytics-ready dataset by merging
CSV, JSON, and SQL sources using LEFT JOINs.

Author: Your Name
"""

import os
import sqlite3
import pandas as pd
from typing import Tuple


DATA_DIR = "data"
OUTPUT_DIR = "output"
OUTPUT_FILE = "final_food_delivery_dataset.csv"


def load_orders() -> pd.DataFrame:
    """Load transactional order data"""
    df = pd.read_csv(os.path.join(DATA_DIR, "orders.csv"))
    return df


def load_users() -> pd.DataFrame:
    """Load user master data"""
    df = pd.read_json(os.path.join(DATA_DIR, "users.json"))
    return df


def load_restaurants() -> pd.DataFrame:
    """Load restaurant master data from SQL"""
    conn = sqlite3.connect(":memory:")
    with open(os.path.join(DATA_DIR, "restaurants.sql"), "r") as f:
        sql_script = f.read()
    conn.executescript(sql_script)

    df = pd.read_sql_query("SELECT * FROM restaurants", conn)
    conn.close()
    return df


def merge_datasets(
    orders: pd.DataFrame,
    users: pd.DataFrame,
    restaurants: pd.DataFrame
) -> pd.DataFrame:
    """Perform LEFT JOINs to retain all orders"""

    orders_users = orders.merge(
        users,
        how="left",
        on="user_id"
    )

    final_df = orders_users.merge(
        restaurants,
        how="left",
        on="restaurant_id"
    )

    return final_df


def save_output(df: pd.DataFrame) -> None:
    """Save final dataset"""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    df.to_csv(os.path.join(OUTPUT_DIR, OUTPUT_FILE), index=False)


def main():
    print("🚀 Starting ETL Pipeline")

    orders = load_orders()
    users = load_users()
    restaurants = load_restaurants()

    final_df = merge_datasets(orders, users, restaurants)
    save_output(final_df)

    print("✅ ETL Completed Successfully")
    print(f"Rows: {final_df.shape[0]}, Columns: {final_df.shape[1]}")


if __name__ == "__main__":
    main()
