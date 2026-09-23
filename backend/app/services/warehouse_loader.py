from __future__ import annotations

import pandas as pd
from sqlalchemy.orm import Session

from app.models.warehouse import (
    DimDate,
    DimCustomer,
    DimProduct,
    DimRegion,
    FactSales,
)


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    df.columns = (
        df.columns
        .astype(str)
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
        .str.replace("-", "_")
    )

    aliases = {
        "date": "order_date",
        "transaction_date": "order_date",
        "sales": "revenue",
        "amount": "revenue",
        "customer": "customer_id",
        "product": "product_id",
        "qty": "quantity",
        "units": "quantity",
    }

    df = df.rename(columns=aliases)

    return df


def require_columns(df: pd.DataFrame) -> None:
    required = {
        "order_id",
        "order_date",
        "customer_id",
        "product_id",
        "quantity",
        "revenue",
        "cost",
        "profit",
        "discount",
    }

    missing = sorted(required - set(df.columns))

    if missing:
        raise ValueError(
            f"Missing required columns: {', '.join(missing)}"
        )


def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    df = normalize_columns(df)

    require_columns(df)

    df["order_date"] = pd.to_datetime(
        df["order_date"],
        errors="coerce",
    )

    numeric_columns = [
        "quantity",
        "revenue",
        "cost",
        "profit",
        "discount",
    ]

    for column in numeric_columns:
        df[column] = pd.to_numeric(
            df[column],
            errors="coerce",
        )

    df = df.dropna(
        subset=[
            "order_id",
            "order_date",
            "customer_id",
            "product_id",
        ]
    )

    df["quantity"] = df["quantity"].fillna(0)
    df["revenue"] = df["revenue"].fillna(0)
    df["cost"] = df["cost"].fillna(0)
    df["profit"] = df["profit"].fillna(
        df["revenue"] - df["cost"]
    )
    df["discount"] = df["discount"].fillna(0)

    return df


def get_or_create_date(
    db: Session,
    order_date,
) -> DimDate:

    existing = (
        db.query(DimDate)
        .filter(DimDate.full_date == order_date.date())
        .first()
    )

    if existing:
        return existing

    date_dimension = DimDate(
        full_date=order_date.date(),
        year=order_date.year,
        month=order_date.month,
        day=order_date.day,
    )

    db.add(date_dimension)
    db.flush()

    return date_dimension


def get_or_create_customer(
    db: Session,
    customer_id,
) -> DimCustomer:

    existing = (
        db.query(DimCustomer)
        .filter(
            DimCustomer.customer_id == str(customer_id)
        )
        .first()
    )

    if existing:
        return existing

    customer = DimCustomer(
        customer_id=str(customer_id),
    )

    db.add(customer)
    db.flush()

    return customer


def get_or_create_product(
    db: Session,
    product_id,
    product_name=None,
    category=None,
) -> DimProduct:

    existing = (
        db.query(DimProduct)
        .filter(
            DimProduct.product_id == str(product_id)
        )
        .first()
    )

    if existing:
        return existing

    product = DimProduct(
        product_id=str(product_id),
        product_name=(
            str(product_name)
            if product_name is not None
            else str(product_id)
        ),
        category=(
            str(category)
            if category is not None
            else "Unknown"
        ),
    )

    db.add(product)
    db.flush()

    return product


def get_or_create_region(
    db: Session,
    region_name,
) -> DimRegion:

    region_name = str(region_name)

    existing = (
        db.query(DimRegion)
        .filter(
            DimRegion.region_name == region_name
        )
        .first()
    )

    if existing:
        return existing

    region = DimRegion(
        region_name=region_name,
    )

    db.add(region)
    db.flush()

    return region


def load_sales_to_warehouse(
    db: Session,
    df: pd.DataFrame,
) -> dict:

    df = clean_dataframe(df)

    loaded = 0
    skipped = 0

    for _, row in df.iterrows():

        existing_order = (
            db.query(FactSales)
            .filter(
                FactSales.order_id
                == str(row["order_id"])
            )
            .first()
        )

        if existing_order:
            skipped += 1
            continue

        date_dimension = get_or_create_date(
            db,
            row["order_date"],
        )

        customer = get_or_create_customer(
            db,
            row["customer_id"],
        )

        product = get_or_create_product(
            db,
            row["product_id"],
            row.get("product_name"),
            row.get("category"),
        )

        region = get_or_create_region(
            db,
            row.get("region", "Unknown"),
        )

        fact = FactSales(
            order_id=str(row["order_id"]),
            date_id=date_dimension.date_id,
            customer_id=customer.customer_id,
            product_id=product.product_id,
            region_id=region.region_id,
            quantity=float(row["quantity"]),
            revenue=float(row["revenue"]),
            cost=float(row["cost"]),
            profit=float(row["profit"]),
            discount=float(row["discount"]),
        )

        db.add(fact)

        loaded += 1

    db.commit()

    return {
        "status": "success",
        "rows_received": len(df),
        "rows_loaded": loaded,
        "rows_skipped": skipped,
    }