import pandas as pd
import sqlite3

DB_PATH = "data/db/supply_chain.db"


def load_data():
    sales = pd.read_csv("data/raw/sales_train_validation.csv")
    calendar = pd.read_csv("data/raw/calendar.csv")
    prices = pd.read_csv("data/raw/sell_prices.csv")
    return sales, calendar, prices


def transform_sales(sales):
    sales_long = sales.melt(
        id_vars=["item_id", "store_id"], var_name="day", value_name="sales"
    )
    return sales_long


def save_to_db(sales, calendar, prices):
    conn = sqlite3.connect(DB_PATH)

    sales.to_sql("sales", conn, if_exists="replace", index=False)
    calendar.to_sql("calendar", conn, if_exists="replace", index=False)
    prices.to_sql("prices", conn, if_exists="replace", index=False)

    conn.close()


def create_demand_table():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.executescript("""
    DROP TABLE IF EXISTS demand;

    CREATE TABLE demand AS
    SELECT 
        s.item_id,
        s.store_id,
        c.date,
        s.sales
    FROM sales s
    JOIN calendar c
    ON s.day = c.d;
    """)

    conn.commit()
    conn.close()


if __name__ == "__main__":
    sales, calendar, prices = load_data()
    sales_long = transform_sales(sales)
    save_to_db(sales_long, calendar, prices)

    create_demand_table()

    print("Data pipeline + demand table created successfully!")
