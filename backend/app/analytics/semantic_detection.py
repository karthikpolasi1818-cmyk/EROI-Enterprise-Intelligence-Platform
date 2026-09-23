from __future__ import annotations

import pandas as pd


PATTERNS = {
    "revenue": [
        "revenue",
        "sales",
        "amount",
        "total_sales",
        "gross_sales",
    ],
    "cost": [
        "cost",
        "expense",
        "cogs",
        "total_cost",
    ],
    "profit": [
        "profit",
        "net_profit",
        "gross_profit",
    ],
    "quantity": [
        "quantity",
        "qty",
        "units",
        "volume",
    ],
    "discount": [
        "discount",
        "discount_rate",
        "discount_pct",
    ],
    "customer": [
        "customer",
        "customer_id",
        "client",
        "client_id",
    ],
    "product": [
        "product",
        "product_id",
        "item",
        "sku",
    ],
    "region": [
        "region",
        "area",
        "territory",
        "zone",
    ],
    "date": [
        "date",
        "order_date",
        "transaction_date",
        "created_at",
    ],
}


def detect_business_semantics(
    df: pd.DataFrame,
) -> dict:

    result = {}

    for column in df.columns:

        normalized = (
            str(column)
            .strip()
            .lower()
            .replace(" ", "_")
            .replace("-", "_")
        )

        detected = []

        for semantic, patterns in PATTERNS.items():

            for pattern in patterns:

                if (
                    normalized == pattern
                    or pattern in normalized
                ):
                    detected.append(semantic)
                    break

        result[str(column)] = {
            "semantic_types": detected,
            "dtype": str(df[column].dtype),
            "unique_values": int(
                df[column].nunique(
                    dropna=True
                )
            ),
        }

    return result