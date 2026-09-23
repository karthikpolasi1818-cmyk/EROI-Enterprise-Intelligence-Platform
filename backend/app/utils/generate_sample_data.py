import random
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd


# ============================================================
# CONFIGURATION
# ============================================================

random.seed(42)

NUMBER_OF_RECORDS = 5000

START_DATE = datetime(2025, 1, 1)

# Find the EROI project root automatically.
# File location:
# eroi-platform/backend/app/utils/generate_sample_data.py
#
# parents[0] = utils
# parents[1] = app
# parents[2] = backend
# parents[3] = eroi-platform
PROJECT_ROOT = Path(__file__).resolve().parents[3]

# Root-level data directory
DATA_DIR = PROJECT_ROOT / "data"

# Output file
OUTPUT_PATH = DATA_DIR / "sample_sales.csv"


# ============================================================
# SAMPLE BUSINESS DATA
# ============================================================

products = [
    ("P001", "Laptop Pro", "Electronics"),
    ("P002", "Wireless Mouse", "Electronics"),
    ("P003", "Keyboard", "Electronics"),
    ("P004", "Office Chair", "Furniture"),
    ("P005", "Desk", "Furniture"),
    ("P006", "Monitor", "Electronics"),
    ("P007", "Notebook", "Stationery"),
    ("P008", "Pen Set", "Stationery"),
]

regions = [
    "North",
    "South",
    "East",
    "West",
]

customers = [
    f"C{str(i).zfill(4)}"
    for i in range(1, 501)
]


# ============================================================
# DATA GENERATION
# ============================================================

records = []

for i in range(1, NUMBER_OF_RECORDS + 1):

    # Select product
    product_id, product_name, category = random.choice(
        products
    )

    # Quantity purchased
    quantity = random.randint(1, 10)

    # Product unit price
    unit_price = random.randint(
        200,
        50000
    )

    # Discount between 0% and 25%
    discount = round(
        random.uniform(0, 0.25),
        2
    )

    # Revenue before discount
    gross_sales = (
        quantity * unit_price
    )

    # Revenue after discount
    sales = round(
        gross_sales * (1 - discount),
        2
    )

    # Cost between 55% and 85% of sales
    cost = round(
        sales * random.uniform(
            0.55,
            0.85
        ),
        2
    )

    # Profit
    profit = round(
        sales - cost,
        2
    )

    # Random order date within one year
    order_date = (
        START_DATE
        + timedelta(
            days=random.randint(
                0,
                364
            )
        )
    )

    # Create record
    records.append(
        {
            "order_id": f"O{str(i).zfill(6)}",

            "order_date": order_date.date(),

            "customer_id": random.choice(
                customers
            ),

            "product_id": product_id,

            "product_name": product_name,

            "category": category,

            "region": random.choice(
                regions
            ),

            "quantity": quantity,

            "sales": sales,

            "cost": cost,

            "profit": profit,

            "discount": discount,
        }
    )


# ============================================================
# CREATE DATAFRAME
# ============================================================

df = pd.DataFrame(records)


# ============================================================
# CREATE DATA DIRECTORY
# ============================================================

DATA_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# SAVE DATASET
# ============================================================

df.to_csv(
    OUTPUT_PATH,
    index=False
)


# ============================================================
# SUMMARY
# ============================================================

print()
print("=" * 60)
print("EROI SAMPLE DATA GENERATOR")
print("=" * 60)

print(
    f"Created records : {len(df):,}"
)

print(
    f"Columns          : {len(df.columns)}"
)

print(
    f"Output file      : {OUTPUT_PATH}"
)

print(
    f"File exists      : {OUTPUT_PATH.exists()}"
)

print()
print("Columns:")

for column in df.columns:
    print(f"  - {column}")

print()
print("=" * 60)
print("DATA GENERATION COMPLETE")
print("=" * 60)