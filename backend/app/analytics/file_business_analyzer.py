from __future__ import annotations

import re
from typing import Any

import pandas as pd


# ============================================================
# BUSINESS SEMANTIC ALIASES
# ============================================================

FIELD_ALIASES = {
    "revenue": [
        "revenue",
        "sales",
        "sale",
        "amount",
        "sales_amount",
        "total_sales",
        "gross_sales",
        "net_sales",
        "turnover",
    ],
    "profit": [
        "profit",
        "net_profit",
        "gross_profit",
        "operating_profit",
        "profit_amount",
    ],
    "cost": [
        "cost",
        "total_cost",
        "cogs",
        "expense",
        "expenses",
        "cost_amount",
    ],
    "quantity": [
        "quantity",
        "qty",
        "units",
        "unit",
        "volume",
        "units_sold",
    ],
    "discount": [
        "discount",
        "discount_rate",
        "discount_pct",
        "discount_percentage",
    ],
    "order_id": [
        "order_id",
        "orderid",
        "order_number",
        "order_no",
        "transaction_id",
        "transactionid",
        "invoice_id",
        "invoice_number",
    ],
    "date": [
        "date",
        "order_date",
        "transaction_date",
        "invoice_date",
        "created_at",
        "created_date",
        "sale_date",
        "sales_date",
    ],
    "customer": [
        "customer",
        "customer_id",
        "customerid",
        "client",
        "client_id",
        "clientid",
    ],
    "product": [
        "product",
        "product_name",
        "product_id",
        "productid",
        "item",
        "item_name",
        "sku",
    ],
    "region": [
        "region",
        "area",
        "territory",
        "zone",
        "location",
        "market",
    ],
    "category": [
        "category",
        "product_category",
        "product_type",
        "segment",
    ],
}


# ============================================================
# NORMALIZATION
# ============================================================

def normalize_column_name(column: Any) -> str:
    value = str(column).strip().lower()

    value = value.replace("%", "pct")
    value = value.replace("₹", "")
    value = value.replace("$", "")
    value = value.replace("€", "")

    value = re.sub(r"[^a-z0-9]+", "_", value)

    return value.strip("_")


def normalize_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    result = df.copy()

    result.columns = [
        normalize_column_name(column)
        for column in result.columns
    ]

    return result


# ============================================================
# SEMANTIC FIELD DETECTION
# ============================================================

def detect_semantic_fields(
    df: pd.DataFrame,
) -> dict[str, str | None]:

    columns = {
        normalize_column_name(column): str(column)
        for column in df.columns
    }

    detected: dict[str, str | None] = {}

    for semantic, aliases in FIELD_ALIASES.items():

        detected[semantic] = None

        # Exact matching
        for alias in aliases:

            alias_normalized = normalize_column_name(alias)

            if alias_normalized in columns:
                detected[semantic] = columns[
                    alias_normalized
                ]
                break

        if detected[semantic]:
            continue

        # Partial matching
        for normalized, original in columns.items():

            for alias in aliases:

                alias_normalized = normalize_column_name(
                    alias
                )

                if (
                    alias_normalized in normalized
                    or normalized in alias_normalized
                ):
                    detected[semantic] = original
                    break

            if detected[semantic]:
                break

    return detected


# ============================================================
# NUMERIC CONVERSION
# ============================================================

def numeric_series(
    df: pd.DataFrame,
    column: str | None,
) -> pd.Series:

    if not column or column not in df.columns:
        return pd.Series(
            0.0,
            index=df.index,
            dtype="float64",
        )

    series = df[column]

    if pd.api.types.is_numeric_dtype(series):
        return pd.to_numeric(
            series,
            errors="coerce",
        ).fillna(0)

    cleaned = (
        series.astype(str)
        .str.replace(",", "", regex=False)
        .str.replace("₹", "", regex=False)
        .str.replace("$", "", regex=False)
        .str.replace("€", "", regex=False)
        .str.replace("%", "", regex=False)
        .str.strip()
    )

    return pd.to_numeric(
        cleaned,
        errors="coerce",
    ).fillna(0)


# ============================================================
# QUALITY
# ============================================================

def calculate_file_quality(
    df: pd.DataFrame,
) -> dict[str, Any]:

    rows = len(df)
    columns = len(df.columns)

    if rows == 0 or columns == 0:
        return {
            "score": 0,
            "status": "EMPTY",
            "rows": rows,
            "columns": columns,
            "missing_cells": 0,
            "missing_rate": 0,
            "duplicate_rows": 0,
            "duplicate_rate": 0,
        }

    total_cells = rows * columns

    missing_cells = int(
        df.isna().sum().sum()
    )

    duplicate_rows = int(
        df.duplicated().sum()
    )

    missing_rate = (
        missing_cells / total_cells
    ) * 100

    duplicate_rate = (
        duplicate_rows / rows
    ) * 100

    score = max(
        0,
        100 - missing_rate - duplicate_rate,
    )

    if score >= 95:
        status = "EXCELLENT"
    elif score >= 85:
        status = "GOOD"
    elif score >= 70:
        status = "WARNING"
    else:
        status = "CRITICAL"

    return {
        "score": round(score, 2),
        "status": status,
        "rows": rows,
        "columns": columns,
        "missing_cells": missing_cells,
        "missing_rate": round(missing_rate, 2),
        "duplicate_rows": duplicate_rows,
        "duplicate_rate": round(duplicate_rate, 2),
    }


# ============================================================
# KPI ANALYSIS
# ============================================================

def calculate_kpis(
    df: pd.DataFrame,
    fields: dict[str, str | None],
) -> dict[str, Any]:

    revenue = numeric_series(
        df,
        fields.get("revenue"),
    )

    profit = numeric_series(
        df,
        fields.get("profit"),
    )

    cost = numeric_series(
        df,
        fields.get("cost"),
    )

    quantity = numeric_series(
        df,
        fields.get("quantity"),
    )

    total_revenue = float(
        revenue.sum()
    )

    total_cost = float(
        cost.sum()
    )

    total_profit = float(
        profit.sum()
    )

    # Derive profit if only revenue + cost exist
    if (
        fields.get("profit") is None
        and fields.get("revenue") is not None
        and fields.get("cost") is not None
    ):
        total_profit = (
            total_revenue - total_cost
        )

    order_column = fields.get(
        "order_id"
    )

    if (
        order_column
        and order_column in df.columns
    ):
        total_orders = int(
            df[order_column]
            .dropna()
            .astype(str)
            .nunique()
        )
    else:
        total_orders = len(df)

    total_quantity = float(
        quantity.sum()
    )

    margin = (
        total_profit
        / total_revenue
        * 100
        if total_revenue
        else 0
    )

    aov = (
        total_revenue
        / total_orders
        if total_orders
        else 0
    )

    return {
        "total_revenue": round(
            total_revenue,
            2,
        ),
        "total_cost": round(
            total_cost,
            2,
        ),
        "total_profit": round(
            total_profit,
            2,
        ),
        "profit_margin": round(
            margin,
            2,
        ),
        "total_orders": int(
            total_orders
        ),
        "total_quantity": round(
            total_quantity,
            2,
        ),
        "aov": round(
            aov,
            2,
        ),
    }


# ============================================================
# MONTHLY
# ============================================================

def calculate_monthly(
    df: pd.DataFrame,
    fields: dict[str, str | None],
) -> list[dict[str, Any]]:

    date_column = fields.get("date")

    if (
        not date_column
        or date_column not in df.columns
    ):
        return []

    work = df.copy()

    work["_eroi_date"] = pd.to_datetime(
        work[date_column],
        errors="coerce",
    )

    work = work.dropna(
        subset=["_eroi_date"]
    )

    if work.empty:
        return []

    work["_month"] = (
        work["_eroi_date"]
        .dt.to_period("M")
        .astype(str)
    )

    work["_revenue"] = numeric_series(
        work,
        fields.get("revenue"),
    )

    work["_profit"] = numeric_series(
        work,
        fields.get("profit"),
    )

    grouped = (
        work.groupby("_month")
        .agg(
            revenue=(
                "_revenue",
                "sum",
            ),
            profit=(
                "_profit",
                "sum",
            ),
            orders=(
                "_month",
                "size",
            ),
        )
        .reset_index()
    )

    return [
        {
            "month": str(
                row["_month"]
            ),
            "revenue": round(
                float(row["revenue"]),
                2,
            ),
            "profit": round(
                float(row["profit"]),
                2,
            ),
            "orders": int(
                row["orders"]
            ),
        }
        for _, row in grouped.iterrows()
    ]


# ============================================================
# REGIONAL
# ============================================================

def calculate_regional(
    df: pd.DataFrame,
    fields: dict[str, str | None],
) -> list[dict[str, Any]]:

    column = fields.get("region")

    if (
        not column
        or column not in df.columns
    ):
        return []

    work = df.copy()

    work["_region"] = (
        work[column]
        .fillna("Unknown")
        .astype(str)
    )

    work["_revenue"] = numeric_series(
        work,
        fields.get("revenue"),
    )

    work["_profit"] = numeric_series(
        work,
        fields.get("profit"),
    )

    grouped = (
        work.groupby("_region")
        .agg(
            revenue=(
                "_revenue",
                "sum",
            ),
            profit=(
                "_profit",
                "sum",
            ),
            orders=(
                "_region",
                "size",
            ),
        )
        .reset_index()
    )

    result = []

    for _, row in grouped.iterrows():

        revenue = float(
            row["revenue"]
        )

        profit = float(
            row["profit"]
        )

        margin = (
            profit / revenue * 100
            if revenue
            else 0
        )

        result.append(
            {
                "region": str(
                    row["_region"]
                ),
                "revenue": round(
                    revenue,
                    2,
                ),
                "profit": round(
                    profit,
                    2,
                ),
                "profit_margin": round(
                    margin,
                    2,
                ),
                "orders": int(
                    row["orders"]
                ),
            }
        )

    return sorted(
        result,
        key=lambda item: item["revenue"],
        reverse=True,
    )


# ============================================================
# PRODUCTS
# ============================================================

def calculate_products(
    df: pd.DataFrame,
    fields: dict[str, str | None],
) -> list[dict[str, Any]]:

    column = fields.get("product")

    if (
        not column
        or column not in df.columns
    ):
        return []

    work = df.copy()

    work["_product"] = (
        work[column]
        .fillna("Unknown")
        .astype(str)
    )

    work["_revenue"] = numeric_series(
        work,
        fields.get("revenue"),
    )

    work["_cost"] = numeric_series(
        work,
        fields.get("cost"),
    )

    work["_profit"] = numeric_series(
        work,
        fields.get("profit"),
    )

    grouped = (
        work.groupby("_product")
        .agg(
            revenue=(
                "_revenue",
                "sum",
            ),
            cost=(
                "_cost",
                "sum",
            ),
            profit=(
                "_profit",
                "sum",
            ),
        )
        .reset_index()
    )

    result = []

    for _, row in grouped.iterrows():

        revenue = float(
            row["revenue"]
        )

        cost = float(
            row["cost"]
        )

        profit = float(
            row["profit"]
        )

        if (
            fields.get("profit") is None
            and fields.get("cost") is not None
        ):
            profit = revenue - cost

        margin = (
            profit / revenue * 100
            if revenue
            else 0
        )

        result.append(
            {
                "product": str(
                    row["_product"]
                ),
                "revenue": round(
                    revenue,
                    2,
                ),
                "cost": round(
                    cost,
                    2,
                ),
                "profit": round(
                    profit,
                    2,
                ),
                "profit_margin": round(
                    margin,
                    2,
                ),
            }
        )

    return sorted(
        result,
        key=lambda item: item["revenue"],
        reverse=True,
    )


# ============================================================
# CATEGORY
# ============================================================

def calculate_categories(
    df: pd.DataFrame,
    fields: dict[str, str | None],
) -> list[dict[str, Any]]:

    column = fields.get("category")

    if (
        not column
        or column not in df.columns
    ):
        return []

    work = df.copy()

    work["_category"] = (
        work[column]
        .fillna("Unknown")
        .astype(str)
    )

    work["_revenue"] = numeric_series(
        work,
        fields.get("revenue"),
    )

    work["_profit"] = numeric_series(
        work,
        fields.get("profit"),
    )

    grouped = (
        work.groupby("_category")
        .agg(
            revenue=(
                "_revenue",
                "sum",
            ),
            profit=(
                "_profit",
                "sum",
            ),
            orders=(
                "_category",
                "size",
            ),
        )
        .reset_index()
    )

    return [
        {
            "category": str(
                row["_category"]
            ),
            "revenue": round(
                float(row["revenue"]),
                2,
            ),
            "profit": round(
                float(row["profit"]),
                2,
            ),
            "orders": int(
                row["orders"]
            ),
        }
        for _, row in grouped.iterrows()
    ]


# ============================================================
# DISCOUNT
# ============================================================

def calculate_discounts(
    df: pd.DataFrame,
    fields: dict[str, str | None],
) -> list[dict[str, Any]]:

    column = fields.get("discount")

    if (
        not column
        or column not in df.columns
    ):
        return []

    work = df.copy()

    work["_discount"] = numeric_series(
        work,
        column,
    )

    work["_revenue"] = numeric_series(
        work,
        fields.get("revenue"),
    )

    work["_profit"] = numeric_series(
        work,
        fields.get("profit"),
    )

    grouped = (
        work.groupby("_discount")
        .agg(
            revenue=(
                "_revenue",
                "sum",
            ),
            profit=(
                "_profit",
                "sum",
            ),
            orders=(
                "_discount",
                "size",
            ),
        )
        .reset_index()
    )

    return [
        {
            "discount": round(
                float(row["_discount"]),
                4,
            ),
            "revenue": round(
                float(row["revenue"]),
                2,
            ),
            "profit": round(
                float(row["profit"]),
                2,
            ),
            "orders": int(
                row["orders"]
            ),
        }
        for _, row in grouped.iterrows()
    ]


# ============================================================
# COMPLETE ANALYSIS
# ============================================================

def analyze_dataframe(
    df: pd.DataFrame,
) -> dict[str, Any]:

    if not isinstance(
        df,
        pd.DataFrame,
    ):
        raise ValueError(
            "Uploaded file is not a tabular dataset."
        )

    clean = normalize_dataframe(
        df
    )

    fields = detect_semantic_fields(
        clean
    )

    quality = calculate_file_quality(
        clean
    )

    kpis = calculate_kpis(
        clean,
        fields,
    )

    monthly = calculate_monthly(
        clean,
        fields,
    )

    regional = calculate_regional(
        clean,
        fields,
    )

    profitability = calculate_products(
        clean,
        fields,
    )

    categories = calculate_categories(
        clean,
        fields,
    )

    discounts = calculate_discounts(
        clean,
        fields,
    )

    ranking = []

    for index, item in enumerate(
        profitability,
        start=1,
    ):
        ranking.append(
            {
                "rank": index,
                "product": item[
                    "product"
                ],
                "revenue": item[
                    "revenue"
                ],
                "profit": item[
                    "profit"
                ],
            }
        )

    return {
        "quality": quality,
        "kpis": kpis,
        "monthly": monthly,
        "regional": regional,
        "profitability": profitability,
        "ranking": ranking,
        "categories": categories,
        "discounts": discounts,
        "semantic_fields": fields,
        "available_semantics": [
            key
            for key, value in fields.items()
            if value is not None
        ],
    }


# ============================================================
# CROSS FILE COMPARISON
# ============================================================

COMPARISON_METRICS = [
    ("Revenue", "total_revenue"),
    ("Profit", "total_profit"),
    ("Profit Margin", "profit_margin"),
    ("Orders", "total_orders"),
    ("Quantity", "total_quantity"),
    ("AOV", "aov"),
]


def compare_business_results(
    file_results: list[dict[str, Any]],
) -> dict[str, Any]:

    metrics = []

    for display_name, key in COMPARISON_METRICS:

        values = []

        for item in file_results:

            kpis = (
                item
                .get("business_analysis", {})
                .get("kpis", {})
            )

            values.append(
                {
                    "filename": item[
                        "filename"
                    ],
                    "value": kpis.get(
                        key,
                        0,
                    ),
                }
            )

        baseline = (
            float(values[0]["value"])
            if values
            else 0
        )

        for index, item in enumerate(
            values
        ):

            value = float(
                item["value"]
            )

            if index == 0:

                item["change"] = 0
                item["change_percent"] = 0

            else:

                change = value - baseline

                change_percent = (
                    change / baseline * 100
                    if baseline
                    else 0
                )

                item["change"] = round(
                    change,
                    2,
                )

                item[
                    "change_percent"
                ] = round(
                    change_percent,
                    2,
                )

        metrics.append(
            {
                "metric": display_name,
                "key": key,
                "values": values,
            }
        )

    semantic_sets = []

    for item in file_results:

        semantic_sets.append(
            set(
                item
                .get("business_analysis", {})
                .get(
                    "available_semantics",
                    [],
                )
            )
        )

    common_business_fields = (
        sorted(
            list(
                set.intersection(
                    *semantic_sets
                )
            )
        )
        if semantic_sets
        else []
    )

    all_business_fields = sorted(
        list(
            set.union(
                *semantic_sets
            )
        )
        if semantic_sets
        else []
    )

    return {
        "semantic_comparison": True,
        "metric_comparison": metrics,
        "common_business_fields": common_business_fields,
        "all_business_fields": all_business_fields,
    }