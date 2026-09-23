from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import inspect, text

from app.db.database import engine


router = APIRouter(
    prefix="/analytics",
    tags=["Business Analytics"],
)


# ============================================================
# DATABASE HELPERS
# ============================================================

def get_table_columns(table_name: str) -> list[str]:
    """
    Return PostgreSQL column names for a table.
    """
    try:
        inspector = inspect(engine)

        return [
            column["name"]
            for column in inspector.get_columns(
                table_name
            )
        ]

    except Exception:
        return []


def table_exists(table_name: str) -> bool:
    try:
        inspector = inspect(engine)

        return inspector.has_table(
            table_name
        )

    except Exception:
        return False


def first_existing_column(
    columns: list[str],
    candidates: list[str],
) -> str | None:

    lower_map = {
        column.lower(): column
        for column in columns
    }

    for candidate in candidates:
        if candidate.lower() in lower_map:
            return lower_map[
                candidate.lower()
            ]

    return None


def quote_identifier(
    identifier: str,
) -> str:
    """
    PostgreSQL-safe identifier quoting.
    Identifiers come only from database
    metadata/candidate lists.
    """
    return '"' + identifier.replace(
        '"',
        '""',
    ) + '"'


def clean_value(
    value: Any,
) -> Any:

    if value is None:
        return None

    if hasattr(
        value,
        "isoformat",
    ):
        return value.isoformat()

    return value


def serialize_row(
    row: Any,
) -> dict:

    mapping = row._mapping

    return {
        str(key): clean_value(value)
        for key, value in mapping.items()
    }


def execute_one(
    sql: str,
    params: dict | None = None,
) -> dict:

    with engine.connect() as connection:
        result = connection.execute(
            text(sql),
            params or {},
        )

        row = result.fetchone()

        if not row:
            return {}

        return serialize_row(row)


def execute_many(
    sql: str,
    params: dict | None = None,
) -> list[dict]:

    with engine.connect() as connection:
        result = connection.execute(
            text(sql),
            params or {},
        )

        return [
            serialize_row(row)
            for row in result.fetchall()
        ]


def require_fact_sales():

    if not table_exists(
        "fact_sales"
    ):
        raise HTTPException(
            status_code=500,
            detail=(
                "fact_sales table does not "
                "exist in the EROI database."
            ),
        )


# ============================================================
# KPI
# ============================================================

@router.get("/kpis")
def get_kpis():

    try:
        require_fact_sales()

        columns = get_table_columns(
            "fact_sales"
        )

        revenue_col = first_existing_column(
            columns,
            [
                "revenue",
                "sales",
                "amount",
            ],
        )

        profit_col = first_existing_column(
            columns,
            [
                "profit",
                "net_profit",
                "gross_profit",
            ],
        )

        quantity_col = first_existing_column(
            columns,
            [
                "quantity",
                "qty",
                "units",
            ],
        )

        order_col = first_existing_column(
            columns,
            [
                "order_id",
                "id",
            ],
        )

        customer_col = first_existing_column(
            columns,
            [
                "customer_id",
                "customer",
                "client_id",
            ],
        )

        if not revenue_col:
            raise HTTPException(
                status_code=500,
                detail=(
                    "Revenue column not found "
                    "in fact_sales."
                ),
            )

        revenue_sql = quote_identifier(
            revenue_col
        )

        profit_expression = (
            f"COALESCE(SUM("
            f"{quote_identifier(profit_col)}"
            f"), 0)"
            if profit_col
            else "0"
        )

        quantity_expression = (
            f"COALESCE(SUM("
            f"{quote_identifier(quantity_col)}"
            f"), 0)"
            if quantity_col
            else "0"
        )

        order_expression = (
            f"COUNT(DISTINCT "
            f"{quote_identifier(order_col)})"
            if order_col
            else "COUNT(*)"
        )

        customer_expression = (
            f"COUNT(DISTINCT "
            f"{quote_identifier(customer_col)})"
            if customer_col
            else "0"
        )

        sql = f"""
        SELECT
            COALESCE(
                SUM({revenue_sql}),
                0
            ) AS total_revenue,

            {profit_expression}
                AS total_profit,

            {quantity_expression}
                AS total_quantity,

            {order_expression}
                AS total_orders,

            {customer_expression}
                AS active_customers

        FROM fact_sales
        """

        result = execute_one(sql)

        total_revenue = float(
            result.get(
                "total_revenue",
                0,
            )
            or 0
        )

        total_profit = float(
            result.get(
                "total_profit",
                0,
            )
            or 0
        )

        total_orders = int(
            result.get(
                "total_orders",
                0,
            )
            or 0
        )

        total_quantity = float(
            result.get(
                "total_quantity",
                0,
            )
            or 0
        )

        active_customers = int(
            result.get(
                "active_customers",
                0,
            )
            or 0
        )

        profit_margin = (
            (
                total_profit
                / total_revenue
            )
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
            "success": True,
            "total_revenue": round(
                total_revenue,
                2,
            ),
            "total_profit": round(
                total_profit,
                2,
            ),
            "profit_margin": round(
                profit_margin,
                2,
            ),
            "total_orders": total_orders,
            "total_quantity": round(
                total_quantity,
                2,
            ),
            "aov": round(
                aov,
                2,
            ),
            "active_customers": active_customers,
        }

    except HTTPException:
        raise

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=(
                "KPI analytics failed: "
                f"{type(exc).__name__}: "
                f"{exc}"
            ),
        ) from exc


# ============================================================
# MONTHLY
# ============================================================

@router.get("/monthly")
def get_monthly():

    try:
        require_fact_sales()

        fact_columns = get_table_columns(
            "fact_sales"
        )

        date_id_col = first_existing_column(
            fact_columns,
            [
                "date_id",
                "date",
                "order_date",
                "transaction_date",
            ],
        )

        revenue_col = first_existing_column(
            fact_columns,
            [
                "revenue",
                "sales",
                "amount",
            ],
        )

        profit_col = first_existing_column(
            fact_columns,
            [
                "profit",
                "net_profit",
                "gross_profit",
            ],
        )

        order_col = first_existing_column(
            fact_columns,
            [
                "order_id",
                "id",
            ],
        )

        if not date_id_col:
            raise HTTPException(
                status_code=500,
                detail=(
                    "date_id/date column not found "
                    "in fact_sales."
                ),
            )

        if not revenue_col:
            raise HTTPException(
                status_code=500,
                detail=(
                    "Revenue column not found "
                    "in fact_sales."
                ),
            )

        date_expression = None

        if table_exists("dim_date"):

            date_columns = get_table_columns(
                "dim_date"
            )

            dim_date_id = first_existing_column(
                date_columns,
                [
                    "date_id",
                    "id",
                ],
            )

            full_date = first_existing_column(
                date_columns,
                [
                    "full_date",
                    "date",
                    "calendar_date",
                ],
            )

            if (
                dim_date_id
                and full_date
            ):

                date_expression = (
                    f'd."{full_date}"'
                )

                join_condition = (
                    f'fs."{date_id_col}" = '
                    f'd."{dim_date_id}"'
                )

            else:
                join_condition = None

        else:
            join_condition = None

        if date_expression is None:

            if "date" in fact_columns:

                date_expression = (
                    f'fs."{date_id_col}"'
                )

                join_condition = None

            else:

                raise HTTPException(
                    status_code=500,
                    detail=(
                        "Unable to resolve a usable "
                        "date column for monthly "
                        "analytics."
                    ),
                )

        profit_expression = (
            f'SUM(fs."{profit_col}")'
            if profit_col
            else "0"
        )

        order_expression = (
            f'COUNT(DISTINCT fs."{order_col}")'
            if order_col
            else "COUNT(*)"
        )

        join_sql = ""

        if join_condition:
            join_sql = (
                "LEFT JOIN dim_date d "
                f"ON {join_condition}"
            )

        sql = f"""
        SELECT
            TO_CHAR(
                DATE_TRUNC(
                    'month',
                    {date_expression}
                ),
                'YYYY-MM'
            ) AS month,

            COALESCE(
                SUM(fs."{revenue_col}"),
                0
            ) AS revenue,

            COALESCE(
                {profit_expression},
                0
            ) AS profit,

            {order_expression}
                AS orders

        FROM fact_sales fs

        {join_sql}

        GROUP BY
            DATE_TRUNC(
                'month',
                {date_expression}
            )

        ORDER BY
            DATE_TRUNC(
                'month',
                {date_expression}
            )
        """

        return {
            "success": True,
            "data": execute_many(sql),
        }

    except HTTPException:
        raise

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=(
                "Monthly analytics failed: "
                f"{type(exc).__name__}: "
                f"{exc}"
            ),
        ) from exc


# ============================================================
# REGIONAL PERFORMANCE
# ============================================================

@router.get("/regional-performance")
def get_regional_performance():

    try:
        require_fact_sales()

        fact_columns = get_table_columns(
            "fact_sales"
        )

        region_id = first_existing_column(
            fact_columns,
            [
                "region_id",
                "region",
            ],
        )

        revenue_col = first_existing_column(
            fact_columns,
            [
                "revenue",
                "sales",
                "amount",
            ],
        )

        profit_col = first_existing_column(
            fact_columns,
            [
                "profit",
                "net_profit",
                "gross_profit",
            ],
        )

        order_col = first_existing_column(
            fact_columns,
            [
                "order_id",
                "id",
            ],
        )

        if not region_id:
            raise HTTPException(
                status_code=500,
                detail=(
                    "region_id/region column "
                    "not found in fact_sales."
                ),
            )

        if not revenue_col:
            raise HTTPException(
                status_code=500,
                detail=(
                    "Revenue column not found."
                ),
            )

        label_expression = (
            f'fs."{region_id}"'
        )

        join_sql = ""

        if table_exists("dim_region"):

            region_columns = get_table_columns(
                "dim_region"
            )

            dim_region_id = first_existing_column(
                region_columns,
                [
                    "region_id",
                    "id",
                ],
            )

            region_name = first_existing_column(
                region_columns,
                [
                    "region_name",
                    "name",
                    "region",
                ],
            )

            if (
                dim_region_id
                and region_name
            ):

                label_expression = (
                    f'dr."{region_name}"'
                )

                join_sql = (
                    "LEFT JOIN dim_region dr "
                    f'ON fs."{region_id}" = '
                    f'dr."{dim_region_id}"'
                )

        profit_expression = (
            f'SUM(fs."{profit_col}")'
            if profit_col
            else "0"
        )

        order_expression = (
            f'COUNT(DISTINCT fs."{order_col}")'
            if order_col
            else "COUNT(*)"
        )

        sql = f"""
        SELECT
            {label_expression}
                AS region,

            COALESCE(
                SUM(fs."{revenue_col}"),
                0
            ) AS revenue,

            COALESCE(
                {profit_expression},
                0
            ) AS profit,

            {order_expression}
                AS orders

        FROM fact_sales fs

        {join_sql}

        GROUP BY
            {label_expression}

        ORDER BY
            revenue DESC
        """

        rows = execute_many(sql)

        for row in rows:

            revenue = float(
                row.get(
                    "revenue",
                    0,
                )
                or 0
            )

            profit = float(
                row.get(
                    "profit",
                    0,
                )
                or 0
            )

            row[
                "profit_margin"
            ] = round(
                (
                    profit
                    / revenue
                    * 100
                )
                if revenue
                else 0,
                2,
            )

        return {
            "success": True,
            "data": rows,
        }

    except HTTPException:
        raise

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=(
                "Regional analytics failed: "
                f"{type(exc).__name__}: "
                f"{exc}"
            ),
        ) from exc


# ============================================================
# PRODUCT PROFITABILITY
# ============================================================

@router.get(
    "/product-profitability"
)
def get_product_profitability():

    try:
        require_fact_sales()

        fact_columns = get_table_columns(
            "fact_sales"
        )

        product_id = first_existing_column(
            fact_columns,
            [
                "product_id",
                "product",
            ],
        )

        revenue_col = first_existing_column(
            fact_columns,
            [
                "revenue",
                "sales",
                "amount",
            ],
        )

        cost_col = first_existing_column(
            fact_columns,
            [
                "cost",
                "expense",
                "cogs",
            ],
        )

        profit_col = first_existing_column(
            fact_columns,
            [
                "profit",
                "net_profit",
                "gross_profit",
            ],
        )

        if not product_id:
            raise HTTPException(
                status_code=500,
                detail=(
                    "product_id/product column "
                    "not found."
                ),
            )

        if not revenue_col:
            raise HTTPException(
                status_code=500,
                detail=(
                    "Revenue column not found."
                ),
            )

        label_expression = (
            f'fs."{product_id}"'
        )

        join_sql = ""

        if table_exists(
            "dim_product"
        ):

            product_columns = (
                get_table_columns(
                    "dim_product"
                )
            )

            dim_product_id = (
                first_existing_column(
                    product_columns,
                    [
                        "product_id",
                        "id",
                    ],
                )
            )

            product_name = (
                first_existing_column(
                    product_columns,
                    [
                        "product_name",
                        "name",
                        "product",
                    ],
                )
            )

            if (
                dim_product_id
                and product_name
            ):

                label_expression = (
                    f'dp."{product_name}"'
                )

                join_sql = (
                    "LEFT JOIN dim_product dp "
                    f'ON fs."{product_id}" = '
                    f'dp."{dim_product_id}"'
                )

        cost_expression = (
            f'SUM(fs."{cost_col}")'
            if cost_col
            else "0"
        )

        profit_expression = (
            f'SUM(fs."{profit_col}")'
            if profit_col
            else "0"
        )

        sql = f"""
        SELECT
            {label_expression}
                AS product,

            COALESCE(
                SUM(fs."{revenue_col}"),
                0
            ) AS revenue,

            COALESCE(
                {cost_expression},
                0
            ) AS cost,

            COALESCE(
                {profit_expression},
                0
            ) AS profit

        FROM fact_sales fs

        {join_sql}

        GROUP BY
            {label_expression}

        ORDER BY
            revenue DESC
        """

        rows = execute_many(sql)

        for row in rows:

            revenue = float(
                row.get(
                    "revenue",
                    0,
                )
                or 0
            )

            profit = float(
                row.get(
                    "profit",
                    0,
                )
                or 0
            )

            row[
                "profit_margin"
            ] = round(
                (
                    profit
                    / revenue
                    * 100
                )
                if revenue
                else 0,
                2,
            )

        return {
            "success": True,
            "data": rows,
        }

    except HTTPException:
        raise

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=(
                "Product profitability failed: "
                f"{type(exc).__name__}: "
                f"{exc}"
            ),
        ) from exc


# ============================================================
# PRODUCT RANKING
# ============================================================

@router.get(
    "/products/ranking"
)
def get_product_ranking(
    limit: int = Query(
        default=10,
        ge=1,
        le=100,
    )
):

    try:
        require_fact_sales()

        fact_columns = get_table_columns(
            "fact_sales"
        )

        product_id = first_existing_column(
            fact_columns,
            [
                "product_id",
                "product",
            ],
        )

        revenue_col = first_existing_column(
            fact_columns,
            [
                "revenue",
                "sales",
                "amount",
            ],
        )

        profit_col = first_existing_column(
            fact_columns,
            [
                "profit",
                "net_profit",
                "gross_profit",
            ],
        )

        if not product_id:
            raise HTTPException(
                status_code=500,
                detail=(
                    "product_id/product column "
                    "not found."
                ),
            )

        if not revenue_col:
            raise HTTPException(
                status_code=500,
                detail=(
                    "Revenue column not found."
                ),
            )

        label_expression = (
            f'fs."{product_id}"'
        )

        join_sql = ""

        if table_exists(
            "dim_product"
        ):

            columns = get_table_columns(
                "dim_product"
            )

            dim_id = first_existing_column(
                columns,
                [
                    "product_id",
                    "id",
                ],
            )

            name = first_existing_column(
                columns,
                [
                    "product_name",
                    "name",
                    "product",
                ],
            )

            if dim_id and name:

                label_expression = (
                    f'dp."{name}"'
                )

                join_sql = (
                    "LEFT JOIN dim_product dp "
                    f'ON fs."{product_id}" = '
                    f'dp."{dim_id}"'
                )

        profit_expression = (
            f'SUM(fs."{profit_col}")'
            if profit_col
            else "0"
        )

        sql = f"""
        SELECT
            {label_expression}
                AS product,

            COALESCE(
                SUM(fs."{revenue_col}"),
                0
            ) AS revenue,

            COALESCE(
                {profit_expression},
                0
            ) AS profit

        FROM fact_sales fs

        {join_sql}

        GROUP BY
            {label_expression}

        ORDER BY
            revenue DESC

        LIMIT :limit
        """

        rows = execute_many(
            sql,
            {
                "limit": limit,
            },
        )

        for index, row in enumerate(
            rows,
            start=1,
        ):
            row["rank"] = index

        return {
            "success": True,
            "data": rows,
        }

    except HTTPException:
        raise

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=(
                "Product ranking failed: "
                f"{type(exc).__name__}: "
                f"{exc}"
            ),
        ) from exc


# ============================================================
# CATEGORIES
# ============================================================

@router.get("/categories")
def get_categories():

    try:
        require_fact_sales()

        fact_columns = get_table_columns(
            "fact_sales"
        )

        product_id = first_existing_column(
            fact_columns,
            [
                "product_id",
                "product",
            ],
        )

        revenue_col = first_existing_column(
            fact_columns,
            [
                "revenue",
                "sales",
                "amount",
            ],
        )

        profit_col = first_existing_column(
            fact_columns,
            [
                "profit",
                "net_profit",
                "gross_profit",
            ],
        )

        order_col = first_existing_column(
            fact_columns,
            [
                "order_id",
                "id",
            ],
        )

        if not product_id:
            raise HTTPException(
                status_code=500,
                detail=(
                    "product_id/product column "
                    "not found."
                ),
            )

        if not revenue_col:
            raise HTTPException(
                status_code=500,
                detail=(
                    "Revenue column not found."
                ),
            )

        category_expression = (
            f'fs."{product_id}"'
        )

        join_sql = ""

        if table_exists(
            "dim_product"
        ):

            columns = get_table_columns(
                "dim_product"
            )

            dim_product_id = (
                first_existing_column(
                    columns,
                    [
                        "product_id",
                        "id",
                    ],
                )
            )

            category_column = (
                first_existing_column(
                    columns,
                    [
                        "category",
                        "product_category",
                        "category_name",
                    ],
                )
            )

            if (
                dim_product_id
                and category_column
            ):

                category_expression = (
                    f'dp."{category_column}"'
                )

                join_sql = (
                    "LEFT JOIN dim_product dp "
                    f'ON fs."{product_id}" = '
                    f'dp."{dim_product_id}"'
                )

        profit_expression = (
            f'SUM(fs."{profit_col}")'
            if profit_col
            else "0"
        )

        order_expression = (
            f'COUNT(DISTINCT fs."{order_col}")'
            if order_col
            else "COUNT(*)"
        )

        sql = f"""
        SELECT
            {category_expression}
                AS category,

            COALESCE(
                SUM(fs."{revenue_col}"),
                0
            ) AS revenue,

            COALESCE(
                {profit_expression},
                0
            ) AS profit,

            {order_expression}
                AS orders

        FROM fact_sales fs

        {join_sql}

        GROUP BY
            {category_expression}

        ORDER BY
            revenue DESC
        """

        return {
            "success": True,
            "data": execute_many(sql),
        }

    except HTTPException:
        raise

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=(
                "Category analytics failed: "
                f"{type(exc).__name__}: "
                f"{exc}"
            ),
        ) from exc


# ============================================================
# DISCOUNTS
# ============================================================

@router.get("/discounts")
def get_discounts():

    try:
        require_fact_sales()

        columns = get_table_columns(
            "fact_sales"
        )

        discount_col = first_existing_column(
            columns,
            [
                "discount",
                "discount_rate",
                "discount_pct",
            ],
        )

        revenue_col = first_existing_column(
            columns,
            [
                "revenue",
                "sales",
                "amount",
            ],
        )

        profit_col = first_existing_column(
            columns,
            [
                "profit",
                "net_profit",
                "gross_profit",
            ],
        )

        order_col = first_existing_column(
            columns,
            [
                "order_id",
                "id",
            ],
        )

        if not discount_col:
            return {
                "success": True,
                "data": [],
                "message": (
                    "No discount column exists "
                    "in fact_sales."
                ),
            }

        if not revenue_col:
            raise HTTPException(
                status_code=500,
                detail=(
                    "Revenue column not found."
                ),
            )

        profit_expression = (
            f'SUM("{profit_col}")'
            if profit_col
            else "0"
        )

        order_expression = (
            f'COUNT(DISTINCT "{order_col}")'
            if order_col
            else "COUNT(*)"
        )

        sql = f"""
        SELECT
            "{discount_col}"
                AS discount,

            COALESCE(
                SUM("{revenue_col}"),
                0
            ) AS revenue,

            COALESCE(
                {profit_expression},
                0
            ) AS profit,

            {order_expression}
                AS orders

        FROM fact_sales

        GROUP BY
            "{discount_col}"

        ORDER BY
            "{discount_col}"
        """

        return {
            "success": True,
            "data": execute_many(sql),
        }

    except HTTPException:
        raise

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=(
                "Discount analytics failed: "
                f"{type(exc).__name__}: "
                f"{exc}"
            ),
        ) from exc


# ============================================================
# FILTER OPTIONS
# ============================================================

@router.get(
    "/filter-options"
)
def get_filter_options():

    try:
        require_fact_sales()

        result = {
            "regions": [],
            "products": [],
            "categories": [],
            "customers": [],
        }

        if table_exists(
            "dim_region"
        ):

            columns = get_table_columns(
                "dim_region"
            )

            name = first_existing_column(
                columns,
                [
                    "region_name",
                    "name",
                    "region",
                ],
            )

            if name:

                rows = execute_many(
                    f"""
                    SELECT DISTINCT
                        "{name}" AS value
                    FROM dim_region
                    WHERE "{name}" IS NOT NULL
                    ORDER BY "{name}"
                    """
                )

                result[
                    "regions"
                ] = [
                    row["value"]
                    for row in rows
                ]

        if table_exists(
            "dim_product"
        ):

            columns = get_table_columns(
                "dim_product"
            )

            name = first_existing_column(
                columns,
                [
                    "product_name",
                    "name",
                    "product",
                ],
            )

            category = first_existing_column(
                columns,
                [
                    "category",
                    "product_category",
                    "category_name",
                ],
            )

            if name:

                rows = execute_many(
                    f"""
                    SELECT DISTINCT
                        "{name}" AS value
                    FROM dim_product
                    WHERE "{name}" IS NOT NULL
                    ORDER BY "{name}"
                    """
                )

                result[
                    "products"
                ] = [
                    row["value"]
                    for row in rows
                ]

            if category:

                rows = execute_many(
                    f"""
                    SELECT DISTINCT
                        "{category}" AS value
                    FROM dim_product
                    WHERE "{category}" IS NOT NULL
                    ORDER BY "{category}"
                    """
                )

                result[
                    "categories"
                ] = [
                    row["value"]
                    for row in rows
                ]

        if table_exists(
            "dim_customer"
        ):

            columns = get_table_columns(
                "dim_customer"
            )

            name = first_existing_column(
                columns,
                [
                    "customer_name",
                    "name",
                    "customer",
                ],
            )

            if name:

                rows = execute_many(
                    f"""
                    SELECT DISTINCT
                        "{name}" AS value
                    FROM dim_customer
                    WHERE "{name}" IS NOT NULL
                    ORDER BY "{name}"
                    """
                )

                result[
                    "customers"
                ] = [
                    row["value"]
                    for row in rows
                ]

        return {
            "success": True,
            **result,
        }

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=(
                "Filter options failed: "
                f"{type(exc).__name__}: "
                f"{exc}"
            ),
        ) from exc


# ============================================================
# OVERVIEW
# ============================================================

@router.get("/overview")
def get_overview():

    try:
        return get_kpis()

    except HTTPException:
        raise

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=(
                "Overview analytics failed: "
                f"{type(exc).__name__}: "
                f"{exc}"
            ),
        ) from exc


# ============================================================
# REGIONS
# ============================================================

@router.get("/regions")
def get_regions():

    return get_regional_performance()


# ============================================================
# PRODUCTS
# ============================================================

@router.get("/products")
def get_products():

    return get_product_profitability()


# ============================================================
# TOP CUSTOMERS
# ============================================================

@router.get(
    "/customers/top"
)
def get_top_customers(
    limit: int = Query(
        default=10,
        ge=1,
        le=100,
    )
):

    try:
        require_fact_sales()

        columns = get_table_columns(
            "fact_sales"
        )

        customer_id = first_existing_column(
            columns,
            [
                "customer_id",
                "customer",
                "client_id",
            ],
        )

        revenue_col = first_existing_column(
            columns,
            [
                "revenue",
                "sales",
                "amount",
            ],
        )

        if not customer_id:
            raise HTTPException(
                status_code=500,
                detail=(
                    "customer_id column "
                    "not found."
                ),
            )

        if not revenue_col:
            raise HTTPException(
                status_code=500,
                detail=(
                    "Revenue column not found."
                ),
            )

        customer_expression = (
            f'fs."{customer_id}"'
        )

        join_sql = ""

        if table_exists(
            "dim_customer"
        ):

            customer_columns = (
                get_table_columns(
                    "dim_customer"
                )
            )

            dim_customer_id = (
                first_existing_column(
                    customer_columns,
                    [
                        "customer_id",
                        "id",
                    ],
                )
            )

            customer_name = (
                first_existing_column(
                    customer_columns,
                    [
                        "customer_name",
                        "name",
                        "customer",
                    ],
                )
            )

            if (
                dim_customer_id
                and customer_name
            ):

                customer_expression = (
                    f'dc."{customer_name}"'
                )

                join_sql = (
                    "LEFT JOIN dim_customer dc "
                    f'ON fs."{customer_id}" = '
                    f'dc."{dim_customer_id}"'
                )

        sql = f"""
        SELECT
            {customer_expression}
                AS customer,

            COALESCE(
                SUM(fs."{revenue_col}"),
                0
            ) AS revenue

        FROM fact_sales fs

        {join_sql}

        GROUP BY
            {customer_expression}

        ORDER BY
            revenue DESC

        LIMIT :limit
        """

        return {
            "success": True,
            "data": execute_many(
                sql,
                {
                    "limit": limit,
                },
            ),
        }

    except HTTPException:
        raise

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=(
                "Customer analytics failed: "
                f"{type(exc).__name__}: "
                f"{exc}"
            ),
        ) from exc