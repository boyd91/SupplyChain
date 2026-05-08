import pandas as pd
import sqlite3
import numpy as np
from pulp import *

DB_PATH = "data/db/supply_chain.db"


# ---------------------------
# 1. LOAD FORECAST
# ---------------------------
def load_forecast():
    conn = sqlite3.connect(DB_PATH)

    query = """
    SELECT *
    FROM forecast
    LIMIT 50000
    """

    df = pd.read_sql(query, conn)
    conn.close()

    return df


# ---------------------------
# 2. ADD COST MODEL
# ---------------------------
def add_cost(df):
    np.random.seed(42)

    df["unit_cost"] = np.random.uniform(5, 20, len(df))
    df["holding_cost"] = df["unit_cost"] * 2
    df["penalty_cost"] = df["unit_cost"] * 1.5

    return df


# ---------------------------
# 3. OPTIMIZATION MODEL
# ---------------------------
def optimize(df):
    n = len(df)

    model = LpProblem("Inventory_Optimization", LpMinimize)

    order = LpVariable.dicts("order", range(n), lowBound=0)
    unmet = LpVariable.dicts("unmet", range(n), lowBound=0)

    # ✅ FIX: objective function (ของจริง)
    model += lpSum(
        df["holding_cost"].iloc[i] * order[i]
        + df["penalty_cost"].iloc[i] * unmet[i]
        for i in range(n)
    )

    # ✅ constraint: warehouse budget
    model += lpSum(
        order[i] * df["unit_cost"].iloc[i] for i in range(n)
    ) <= 450000

    # unmet demand definition
    for i in range(n):
        model += unmet[i] >= df["forecast"].iloc[i] - order[i]

    # service level (optional)
    for i in range(n):
        model += order[i] >= 0.2 * df["forecast"].iloc[i]

    model.solve()

    df["optimized_order"] = [order[i].value() for i in range(n)]
    df["unmet_demand"] = [unmet[i].value() for i in range(n)]

    print("\nDEBUG:")
    print(df[["forecast", "optimized_order", "unmet_demand"]].head())

    return df


# ---------------------------
# 4. COST COMPARISON
# ---------------------------
def calculate_cost(df):
    df["baseline_order"] = df["forecast"]

    df["cost_before"] = df["baseline_order"] * df["holding_cost"]
    df["cost_after"] = (
        df["optimized_order"] * df["holding_cost"]
        + df["unmet_demand"] * df["penalty_cost"]
    )
    total_before = df["cost_before"].sum()
    total_after = df["cost_after"].sum()
    saving = total_before - total_after

    print("\n===== COST SUMMARY =====")
    print(f"Before Cost : {total_before:,.2f}")
    print(f"After Cost  : {total_after:,.2f}")
    print(f"Savings     : {saving:,.2f}")
    print("========================\n")

    return df


# ---------------------------
# 5. SAVE RESULT
# ---------------------------
def save_result(df):
    conn = sqlite3.connect(DB_PATH)
    df.to_sql("optimization_result", conn, if_exists="replace", index=False)
    conn.close()


# ---------------------------
# MAIN PIPELINE
# ---------------------------
if __name__ == "__main__":
    print("Loading forecast...")
    df = load_forecast()

    print("Adding cost model...")
    df = add_cost(df)

    print("Running optimization...")
    df = optimize(df)

    print("Calculating cost...")
    df = calculate_cost(df)

    print("Saving results to DB...")
    save_result(df)

    print("Exporting to CSV...")
    df.to_csv("optimization_result.csv", index=False)

    print("Optimization completed successfully!")
