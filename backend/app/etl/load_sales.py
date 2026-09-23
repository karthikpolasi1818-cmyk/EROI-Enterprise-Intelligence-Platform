from pathlib import Path

import pandas as pd
from sqlalchemy import func, select

from app.db.database import SessionLocal
from app.models.warehouse import (
    DimCustomer,
    DimDate,
    DimProduct,
    DimRegion,
    FactSales,
)


PROJECT_ROOT = Path(__file__).resolve().parents[3]
CSV_PATH = PROJECT_ROOT / "data" / "sample_sales.csv"


REGION_MAP = {
    "North": 1,
    "South": 2,
    "East": 3,
    "West": 4,
}


def load_data():
    print("=" * 60)
    print("EROI ETL PIPELINE")
    print("=" * 60)

    # ---------------------------------------------------------
    # 1. Extract
    # ---------------------------------------------------------
    print("\n[1/5] Extracting data...")

    if not CSV_PATH.exists():
        raise FileNotFoundError(f"Dataset not found: {CSV_PATH}")

    df = pd.read_csv(CSV_PATH)

    print(f"Source file : {CSV_PATH}")
    print(f"Rows        : {len(df):,}")
    print(f"Columns     : {len(df.columns)}")

    # ---------------------------------------------------------
    # 2. Transform
    # ---------------------------------------------------------
    print("\n[2/5] Transforming data...")

    df["order_date"] = pd.to_datetime(df["order_date"])

    df["region_id"] = df["region"].map(REGION_MAP)

    if df["region_id"].isna().any():
        raise ValueError("Unknown region found in dataset.")

    df["date_id"] = (
        df["order_date"].dt.year * 10000
        + df["order_date"].dt.month * 100
        + df["order_date"].dt.day
    )

    df["revenue"] = df["sales"]

    print("Date transformation complete.")
    print("Revenue standardized from sales.")
    print("Region IDs generated.")

    # ---------------------------------------------------------
    # 3. Database session
    # ---------------------------------------------------------
    print("\n[3/5] Connecting to PostgreSQL...")

    db = SessionLocal()

    try:
        # -----------------------------------------------------
        # 4. Load dimensions
        # -----------------------------------------------------
        print("\n[4/5] Loading dimension tables...")

        # Date dimension
        dates = (
            df[
                [
                    "date_id",
                    "order_date",
                ]
            ]
            .drop_duplicates()
            .sort_values("order_date")
        )

        for row in dates.itertuples(index=False):
            existing = db.get(DimDate, int(row.date_id))

            if existing is None:
                db.add(
                    DimDate(
                        date_id=int(row.date_id),
                        full_date=row.order_date.date(),
                        year=int(row.order_date.year),
                        quarter=int(row.order_date.quarter),
                        month=int(row.order_date.month),
                        month_name=row.order_date.strftime("%B"),
                        week=int(row.order_date.isocalendar().week),
                        day=int(row.order_date.day),
                    )
                )

        # Customer dimension
        customers = df["customer_id"].drop_duplicates()

        for customer_id in customers:
            if db.get(DimCustomer, customer_id) is None:
                db.add(
                    DimCustomer(
                        customer_id=customer_id,
                    )
                )

        # Product dimension
        products = (
            df[
                [
                    "product_id",
                    "product_name",
                    "category",
                ]
            ]
            .drop_duplicates(subset=["product_id"])
        )

        for row in products.itertuples(index=False):
            if db.get(DimProduct, row.product_id) is None:
                db.add(
                    DimProduct(
                        product_id=row.product_id,
                        product_name=row.product_name,
                        category=row.category,
                    )
                )

        # Region dimension
        for region_name, region_id in REGION_MAP.items():
            existing = db.get(DimRegion, region_id)

            if existing is None:
                db.add(
                    DimRegion(
                        region_id=region_id,
                        region_name=region_name,
                    )
                )

        db.commit()

        print(f"Dates loaded    : {len(dates):,}")
        print(f"Customers loaded: {len(customers):,}")
        print(f"Products loaded : {len(products):,}")
        print(f"Regions loaded  : {len(REGION_MAP):,}")

        # -----------------------------------------------------
        # Fact table
        # -----------------------------------------------------
        print("\nLoading fact_sales...")

        existing_orders = set(
            db.execute(
                select(FactSales.order_id)
            ).scalars().all()
        )

        fact_count = 0

        for row in df.itertuples(index=False):

            if row.order_id in existing_orders:
                continue

            db.add(
                FactSales(
                    order_id=row.order_id,
                    date_id=int(row.date_id),
                    customer_id=row.customer_id,
                    product_id=row.product_id,
                    region_id=int(row.region_id),
                    quantity=int(row.quantity),
                    revenue=float(row.revenue),
                    cost=float(row.cost),
                    profit=float(row.profit),
                    discount=float(row.discount),
                )
            )

            fact_count += 1

        db.commit()

        print(f"Fact rows inserted: {fact_count:,}")

        # -----------------------------------------------------
        # 5. Validation
        # -----------------------------------------------------
        print("\n[5/5] Validating warehouse...")

        total_facts = db.scalar(
            select(func.count()).select_from(FactSales)
        )

        total_revenue = db.scalar(
            select(func.sum(FactSales.revenue))
        )

        total_profit = db.scalar(
            select(func.sum(FactSales.profit))
        )

        print(f"Fact sales rows : {total_facts:,}")
        print(f"Total revenue   : {total_revenue:,.2f}")
        print(f"Total profit    : {total_profit:,.2f}")

        print("\n" + "=" * 60)
        print("ETL PIPELINE COMPLETED SUCCESSFULLY")
        print("=" * 60)

    finally:
        db.close()


if __name__ == "__main__":
    load_data()