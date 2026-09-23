from sqlalchemy import (
    Column,
    Integer,
    Float,
    String,
    Date,
    ForeignKey
)

from app.db.database import Base


class DimDate(Base):
    __tablename__ = "dim_date"

    date_id = Column(Integer, primary_key=True, index=True)
    full_date = Column(Date, unique=True)
    year = Column(Integer)
    month = Column(Integer)
    day = Column(Integer)


class DimCustomer(Base):
    __tablename__ = "dim_customer"

    customer_id = Column(String, primary_key=True)
    customer_name = Column(String, nullable=True)


class DimProduct(Base):
    __tablename__ = "dim_product"

    product_id = Column(String, primary_key=True)
    product_name = Column(String)
    category = Column(String)


class DimRegion(Base):
    __tablename__ = "dim_region"

    region_id = Column(Integer, primary_key=True, index=True)
    region_name = Column(String, unique=True)


class FactSales(Base):
    __tablename__ = "fact_sales"

    id = Column(Integer, primary_key=True, index=True)

    order_id = Column(String, unique=True)

    date_id = Column(Integer, ForeignKey("dim_date.date_id"))

    customer_id = Column(
        String,
        ForeignKey("dim_customer.customer_id")
    )

    product_id = Column(
        String,
        ForeignKey("dim_product.product_id")
    )

    region_id = Column(
        Integer,
        ForeignKey("dim_region.region_id")
    )

    quantity = Column(Float)
    revenue = Column(Float)
    cost = Column(Float)
    profit = Column(Float)
    discount = Column(Float)