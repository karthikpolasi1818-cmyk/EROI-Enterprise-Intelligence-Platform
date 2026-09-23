from datetime import date

from fastapi import APIRouter, Query
from sqlalchemy import distinct, func, select

from app.db.database import SessionLocal
from app.models.warehouse import (
    DimCustomer,
    DimDate,
    DimProduct,
    DimRegion,
    FactSales,
)


router = APIRouter(
    prefix="/analytics",
    tags=["Advanced Analytics"],
)


# ============================================================
# COMMON FILTER HELPER
# ============================================================

def apply_filters(
    statement,
    start_date: date | None = None,
    end_date: date | None = None,
    region: str | None = None,
    category: str | None = None,
):
    """
    Apply common filters to analytics queries.
    """

    if start_date is not None:
        statement = statement.where(
            DimDate.full_date >= start_date
        )

    if end_date is not None:
        statement = statement.where(
            DimDate.full_date <= end_date
        )

    if region is not None and region.lower() != "all":
        statement = statement.where(
            DimRegion.region_name == region
        )

    if category is not None and category.lower() != "all":
        statement = statement.where(
            DimProduct.category == category
        )

    return statement


# ============================================================
# FILTER OPTIONS
# ============================================================

@router.get("/filter-options")
def filter_options():
    """
    Return available regions, categories and date range.
    """

    db = SessionLocal()

    try:
        regions = db.execute(
            select(DimRegion.region_name)
            .order_by(DimRegion.region_name)
        ).scalars().all()

        categories = db.execute(
            select(DimProduct.category)
            .distinct()
            .order_by(DimProduct.category)
        ).scalars().all()

        min_date = db.scalar(
            select(func.min(DimDate.full_date))
        )

        max_date = db.scalar(
            select(func.max(DimDate.full_date))
        )

        return {
            "success": True,
            "filters": {
                "regions": list(regions),
                "categories": list(categories),
                "min_date": (
                    min_date.isoformat()
                    if min_date
                    else None
                ),
                "max_date": (
                    max_date.isoformat()
                    if max_date
                    else None
                ),
            },
        }

    finally:
        db.close()


# ============================================================
# KPI SUMMARY
# ============================================================

@router.get("/kpis")
def kpi_summary(
    start_date: date | None = Query(default=None),
    end_date: date | None = Query(default=None),
    region: str | None = Query(default=None),
    category: str | None = Query(default=None),
):
    db = SessionLocal()

    try:
        statement = (
            select(
                func.coalesce(
                    func.sum(FactSales.revenue),
                    0,
                ).label("revenue"),

                func.coalesce(
                    func.sum(FactSales.cost),
                    0,
                ).label("cost"),

                func.coalesce(
                    func.sum(FactSales.profit),
                    0,
                ).label("profit"),

                func.count(
                    FactSales.sale_id
                ).label("orders"),

                func.coalesce(
                    func.sum(FactSales.quantity),
                    0,
                ).label("quantity"),

                func.count(
                    distinct(FactSales.customer_id)
                ).label("customers"),

                func.count(
                    distinct(FactSales.product_id)
                ).label("products"),
            )
            .select_from(FactSales)
            .join(
                DimDate,
                FactSales.date_id == DimDate.date_id,
            )
            .join(
                DimRegion,
                FactSales.region_id == DimRegion.region_id,
            )
            .join(
                DimProduct,
                FactSales.product_id
                == DimProduct.product_id,
            )
        )

        statement = apply_filters(
            statement,
            start_date,
            end_date,
            region,
            category,
        )

        row = db.execute(statement).one()

        revenue = float(row.revenue or 0)
        cost = float(row.cost or 0)
        profit = float(row.profit or 0)
        orders = int(row.orders or 0)
        quantity = int(row.quantity or 0)
        customers = int(row.customers or 0)
        products = int(row.products or 0)

        profit_margin = (
            (profit / revenue) * 100
            if revenue
            else 0
        )

        average_order_value = (
            revenue / orders
            if orders
            else 0
        )

        average_revenue_per_customer = (
            revenue / customers
            if customers
            else 0
        )

        average_quantity_per_order = (
            quantity / orders
            if orders
            else 0
        )

        return {
            "success": True,

            "filters": {
                "start_date": (
                    start_date.isoformat()
                    if start_date
                    else None
                ),
                "end_date": (
                    end_date.isoformat()
                    if end_date
                    else None
                ),
                "region": region,
                "category": category,
            },

            "kpis": {
                "total_revenue": round(
                    revenue,
                    2,
                ),
                "total_cost": round(
                    cost,
                    2,
                ),
                "total_profit": round(
                    profit,
                    2,
                ),
                "total_orders": orders,
                "total_quantity": quantity,
                "total_customers": customers,
                "total_products": products,

                "profit_margin": round(
                    profit_margin,
                    2,
                ),

                "average_order_value": round(
                    average_order_value,
                    2,
                ),

                "average_revenue_per_customer": round(
                    average_revenue_per_customer,
                    2,
                ),

                "average_quantity_per_order": round(
                    average_quantity_per_order,
                    2,
                ),
            },
        }

    finally:
        db.close()


# ============================================================
# MONTHLY ANALYTICS
# ============================================================

@router.get("/monthly")
def monthly_analytics(
    start_date: date | None = Query(default=None),
    end_date: date | None = Query(default=None),
    region: str | None = Query(default=None),
    category: str | None = Query(default=None),
):
    db = SessionLocal()

    try:
        statement = (
            select(
                DimDate.year,
                DimDate.month,
                DimDate.month_name,

                func.sum(
                    FactSales.revenue
                ).label("revenue"),

                func.sum(
                    FactSales.cost
                ).label("cost"),

                func.sum(
                    FactSales.profit
                ).label("profit"),

                func.count(
                    FactSales.sale_id
                ).label("orders"),

                func.sum(
                    FactSales.quantity
                ).label("quantity"),
            )
            .select_from(FactSales)
            .join(
                DimDate,
                FactSales.date_id == DimDate.date_id,
            )
            .join(
                DimRegion,
                FactSales.region_id
                == DimRegion.region_id,
            )
            .join(
                DimProduct,
                FactSales.product_id
                == DimProduct.product_id,
            )
        )

        statement = apply_filters(
            statement,
            start_date,
            end_date,
            region,
            category,
        )

        statement = (
            statement
            .group_by(
                DimDate.year,
                DimDate.month,
                DimDate.month_name,
            )
            .order_by(
                DimDate.year,
                DimDate.month,
            )
        )

        rows = db.execute(statement).all()

        return {
            "success": True,
            "data": [
                {
                    "year": int(row.year),
                    "month": int(row.month),
                    "month_name": row.month_name,

                    "revenue": round(
                        float(row.revenue or 0),
                        2,
                    ),

                    "cost": round(
                        float(row.cost or 0),
                        2,
                    ),

                    "profit": round(
                        float(row.profit or 0),
                        2,
                    ),

                    "orders": int(
                        row.orders or 0
                    ),

                    "quantity": int(
                        row.quantity or 0
                    ),
                }
                for row in rows
            ],
        }

    finally:
        db.close()


# ============================================================
# CATEGORY ANALYTICS
# ============================================================

@router.get("/categories")
def category_analytics(
    start_date: date | None = Query(default=None),
    end_date: date | None = Query(default=None),
    region: str | None = Query(default=None),
    category: str | None = Query(default=None),
):
    db = SessionLocal()

    try:
        statement = (
            select(
                DimProduct.category,

                func.sum(
                    FactSales.revenue
                ).label("revenue"),

                func.sum(
                    FactSales.cost
                ).label("cost"),

                func.sum(
                    FactSales.profit
                ).label("profit"),

                func.sum(
                    FactSales.quantity
                ).label("quantity"),

                func.count(
                    FactSales.sale_id
                ).label("orders"),
            )
            .select_from(FactSales)
            .join(
                DimDate,
                FactSales.date_id == DimDate.date_id,
            )
            .join(
                DimRegion,
                FactSales.region_id
                == DimRegion.region_id,
            )
            .join(
                DimProduct,
                FactSales.product_id
                == DimProduct.product_id,
            )
        )

        statement = apply_filters(
            statement,
            start_date,
            end_date,
            region,
            category,
        )

        statement = (
            statement
            .group_by(DimProduct.category)
            .order_by(
                func.sum(
                    FactSales.revenue
                ).desc()
            )
        )

        rows = db.execute(statement).all()

        data = []

        for row in rows:
            revenue = float(
                row.revenue or 0
            )

            profit = float(
                row.profit or 0
            )

            data.append(
                {
                    "category": row.category,

                    "revenue": round(
                        revenue,
                        2,
                    ),

                    "cost": round(
                        float(row.cost or 0),
                        2,
                    ),

                    "profit": round(
                        profit,
                        2,
                    ),

                    "quantity": int(
                        row.quantity or 0
                    ),

                    "orders": int(
                        row.orders or 0
                    ),

                    "profit_margin": round(
                        (
                            profit / revenue
                        ) * 100
                        if revenue
                        else 0,
                        2,
                    ),
                }
            )

        return {
            "success": True,
            "data": data,
        }

    finally:
        db.close()


# ============================================================
# REGIONAL PERFORMANCE
# ============================================================

@router.get("/regional-performance")
def regional_performance(
    start_date: date | None = Query(default=None),
    end_date: date | None = Query(default=None),
    region: str | None = Query(default=None),
    category: str | None = Query(default=None),
):
    db = SessionLocal()

    try:
        statement = (
            select(
                DimRegion.region_name.label(
                    "region"
                ),

                func.sum(
                    FactSales.revenue
                ).label("revenue"),

                func.sum(
                    FactSales.cost
                ).label("cost"),

                func.sum(
                    FactSales.profit
                ).label("profit"),

                func.sum(
                    FactSales.quantity
                ).label("quantity"),

                func.count(
                    FactSales.sale_id
                ).label("orders"),
            )
            .select_from(FactSales)
            .join(
                DimDate,
                FactSales.date_id == DimDate.date_id,
            )
            .join(
                DimRegion,
                FactSales.region_id
                == DimRegion.region_id,
            )
            .join(
                DimProduct,
                FactSales.product_id
                == DimProduct.product_id,
            )
        )

        statement = apply_filters(
            statement,
            start_date,
            end_date,
            region,
            category,
        )

        statement = (
            statement
            .group_by(
                DimRegion.region_name
            )
            .order_by(
                func.sum(
                    FactSales.revenue
                ).desc()
            )
        )

        rows = db.execute(statement).all()

        data = []

        for row in rows:
            revenue = float(
                row.revenue or 0
            )

            profit = float(
                row.profit or 0
            )

            data.append(
                {
                    "region": row.region,

                    "revenue": round(
                        revenue,
                        2,
                    ),

                    "cost": round(
                        float(row.cost or 0),
                        2,
                    ),

                    "profit": round(
                        profit,
                        2,
                    ),

                    "quantity": int(
                        row.quantity or 0
                    ),

                    "orders": int(
                        row.orders or 0
                    ),

                    "profit_margin": round(
                        (
                            profit / revenue
                        ) * 100
                        if revenue
                        else 0,
                        2,
                    ),
                }
            )

        return {
            "success": True,
            "data": data,
        }

    finally:
        db.close()


# ============================================================
# PRODUCT PROFITABILITY
# ============================================================

@router.get("/product-profitability")
def product_profitability(
    start_date: date | None = Query(default=None),
    end_date: date | None = Query(default=None),
    region: str | None = Query(default=None),
    category: str | None = Query(default=None),
):
    db = SessionLocal()

    try:
        statement = (
            select(
                DimProduct.product_id,
                DimProduct.product_name,
                DimProduct.category,

                func.sum(
                    FactSales.revenue
                ).label("revenue"),

                func.sum(
                    FactSales.cost
                ).label("cost"),

                func.sum(
                    FactSales.profit
                ).label("profit"),

                func.sum(
                    FactSales.quantity
                ).label("quantity"),
            )
            .select_from(FactSales)
            .join(
                DimDate,
                FactSales.date_id == DimDate.date_id,
            )
            .join(
                DimRegion,
                FactSales.region_id
                == DimRegion.region_id,
            )
            .join(
                DimProduct,
                FactSales.product_id
                == DimProduct.product_id,
            )
        )

        statement = apply_filters(
            statement,
            start_date,
            end_date,
            region,
            category,
        )

        statement = (
            statement
            .group_by(
                DimProduct.product_id,
                DimProduct.product_name,
                DimProduct.category,
            )
            .order_by(
                func.sum(
                    FactSales.revenue
                ).desc()
            )
        )

        rows = db.execute(statement).all()

        data = []

        for row in rows:
            revenue = float(
                row.revenue or 0
            )

            profit = float(
                row.profit or 0
            )

            data.append(
                {
                    "product_id": row.product_id,
                    "product_name": row.product_name,
                    "category": row.category,

                    "revenue": round(
                        revenue,
                        2,
                    ),

                    "cost": round(
                        float(row.cost or 0),
                        2,
                    ),

                    "profit": round(
                        profit,
                        2,
                    ),

                    "quantity": int(
                        row.quantity or 0
                    ),

                    "profit_margin": round(
                        (
                            profit / revenue
                        ) * 100
                        if revenue
                        else 0,
                        2,
                    ),
                }
            )

        return {
            "success": True,
            "data": data,
        }

    finally:
        db.close()


# ============================================================
# PRODUCT RANKING
# ============================================================

@router.get("/products/ranking")
def product_ranking(
    limit: int = Query(
        default=5,
        ge=1,
        le=100,
    ),
    start_date: date | None = Query(default=None),
    end_date: date | None = Query(default=None),
    region: str | None = Query(default=None),
    category: str | None = Query(default=None),
):
    """
    Rank products by revenue.

    Returns:
        - Top products
        - Bottom products
        - Actual overall rank
        - Total product count
    """

    db = SessionLocal()

    try:
        statement = (
            select(
                DimProduct.product_id,
                DimProduct.product_name,
                DimProduct.category,

                func.sum(
                    FactSales.revenue
                ).label("revenue"),

                func.sum(
                    FactSales.profit
                ).label("profit"),
            )
            .select_from(FactSales)
            .join(
                DimDate,
                FactSales.date_id
                == DimDate.date_id,
            )
            .join(
                DimRegion,
                FactSales.region_id
                == DimRegion.region_id,
            )
            .join(
                DimProduct,
                FactSales.product_id
                == DimProduct.product_id,
            )
        )

        statement = apply_filters(
            statement,
            start_date,
            end_date,
            region,
            category,
        )

        statement = (
            statement
            .group_by(
                DimProduct.product_id,
                DimProduct.product_name,
                DimProduct.category,
            )
            .order_by(
                func.sum(
                    FactSales.revenue
                ).desc()
            )
        )

        rows = db.execute(
            statement
        ).all()

        # ----------------------------------------------------
        # Build complete ranking first
        # ----------------------------------------------------

        all_products = []

        for index, row in enumerate(rows):

            all_products.append(
                {
                    "rank": index + 1,

                    "product_id": row.product_id,

                    "product_name": row.product_name,

                    "category": row.category,

                    "revenue": round(
                        float(
                            row.revenue or 0
                        ),
                        2,
                    ),

                    "profit": round(
                        float(
                            row.profit or 0
                        ),
                        2,
                    ),
                }
            )

        # ----------------------------------------------------
        # Top products
        # ----------------------------------------------------

        top_products = all_products[
            :limit
        ]

        # ----------------------------------------------------
        # Bottom products
        #
        # Because all_products is already ranked DESC,
        # the last records represent the lowest revenue.
        #
        # Their original rank is preserved.
        # ----------------------------------------------------

        bottom_products = all_products[
            -limit:
        ]

        return {
            "success": True,

            "total_products": len(
                all_products
            ),

            "top_products": top_products,

            "bottom_products": bottom_products,
        }

    finally:
        db.close()


# ============================================================
# DISCOUNT ANALYSIS
# ============================================================

@router.get("/discounts")
def discount_analysis(
    start_date: date | None = Query(default=None),
    end_date: date | None = Query(default=None),
    region: str | None = Query(default=None),
    category: str | None = Query(default=None),
):
    db = SessionLocal()

    try:
        statement = (
            select(
                FactSales.discount.label(
                    "discount"
                ),

                func.sum(
                    FactSales.revenue
                ).label("revenue"),

                func.sum(
                    FactSales.profit
                ).label("profit"),

                func.count(
                    FactSales.sale_id
                ).label("orders"),
            )
            .select_from(FactSales)
            .join(
                DimDate,
                FactSales.date_id
                == DimDate.date_id,
            )
            .join(
                DimRegion,
                FactSales.region_id
                == DimRegion.region_id,
            )
            .join(
                DimProduct,
                FactSales.product_id
                == DimProduct.product_id,
            )
        )

        statement = apply_filters(
            statement,
            start_date,
            end_date,
            region,
            category,
        )

        statement = (
            statement
            .group_by(
                FactSales.discount
            )
            .order_by(
                FactSales.discount
            )
        )

        rows = db.execute(
            statement
        ).all()

        data = []

        for row in rows:
            revenue = float(
                row.revenue or 0
            )

            profit = float(
                row.profit or 0
            )

            data.append(
                {
                    "discount": round(
                        float(
                            row.discount
                        ) * 100,
                        2,
                    ),

                    "revenue": round(
                        revenue,
                        2,
                    ),

                    "profit": round(
                        profit,
                        2,
                    ),

                    "orders": int(
                        row.orders or 0
                    ),

                    "profit_margin": round(
                        (
                            profit / revenue
                        ) * 100
                        if revenue
                        else 0,
                        2,
                    ),
                }
            )

        return {
            "success": True,
            "data": data,
        }

    finally:
        db.close()