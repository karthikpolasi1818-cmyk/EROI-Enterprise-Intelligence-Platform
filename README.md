\# EROI — Enterprise Revenue \& Operations Intelligence Platform



<p align="center">



\*\*Enterprise-grade analytics platform for transforming raw business data into revenue, profitability, operational, and comparative intelligence.\*\*



</p>



<p align="center">



!\[Python](https://img.shields.io/badge/Python-3.12+-3776AB?style=for-the-badge\&logo=python\&logoColor=white)

!\[FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688?style=for-the-badge\&logo=fastapi\&logoColor=white)

!\[Next.js](https://img.shields.io/badge/Next.js-Frontend-000000?style=for-the-badge\&logo=next.js\&logoColor=white)

!\[TypeScript](https://img.shields.io/badge/TypeScript-Frontend-3178C6?style=for-the-badge\&logo=typescript\&logoColor=white)

!\[PostgreSQL](https://img.shields.io/badge/PostgreSQL-Warehouse-4169E1?style=for-the-badge\&logo=postgresql\&logoColor=white)

!\[Pandas](https://img.shields.io/badge/Pandas-Analytics-150458?style=for-the-badge\&logo=pandas\&logoColor=white)



</p>



\---



\## Overview



\*\*EROI (Enterprise Revenue \& Operations Intelligence)\*\* is a full-stack business intelligence platform designed to transform heterogeneous business datasets into structured, decision-ready analytics.



The platform combines automated data ingestion, data profiling, data quality assessment, semantic business-field detection, KPI computation, business analytics, PostgreSQL warehousing, and multi-file comparison into a single system.



\### Core Pipeline



```text

Raw Business Data

&#x20;       ↓

Universal Data Ingestion

&#x20;       ↓

Dataset Profiling

&#x20;       ↓

Data Quality Assessment

&#x20;       ↓

Semantic Business Detection

&#x20;       ↓

KPI \& Metric Computation

&#x20;       ↓

Revenue / Profit / Operations Analytics

&#x20;       ↓

Business Comparison

&#x20;       ↓

Interactive Dashboard

Why EROI?

Organizations often work with business information distributed across different files and schemas.

EROI addresses the problem of converting this raw information into structured business intelligence.

The platform can analyze:

\- Revenue

\- Profit

\- Profit Margin

\- Orders

\- Quantity

\- Customers

\- Products

\- Regions

\- Categories

\- Discounts

\- Time-based performance

It also evaluates the quality and structure of the underlying data before generating business metrics.

Key Capabilities

1\. Universal Data Ingestion

EROI provides a unified ingestion layer for heterogeneous business data.

Supported formats

\- CSV

\- XLSX

\- XLS

\- JSON

\- Parquet

\- PDF

\- DOCX

\- PPTX

\- TXT

\- Markdown

\- LOG

\- XML

\- HTML

2\. Automated Data Profiling

The platform automatically profiles uploaded datasets.

It identifies:

\- Dataset dimensions

\- Column names

\- Data types

\- Numeric fields

\- Missing values

\- Duplicate records

\- Potential outliers

\- Business-related fields

3\. Data Quality Intelligence

EROI evaluates the reliability of incoming datasets.

Current quality checks include:

\- Missing-cell detection

\- Missing-rate calculation

\- Duplicate-row detection

\- Duplicate-rate calculation

\- Numeric outlier detection

\- Overall quality scoring

This allows analytical results to be considered together with the quality of the source data.

Semantic Business Detection

One of EROI's key capabilities is automated semantic field detection.

Instead of requiring users to manually configure every dataset, the platform identifies business concepts such as:

Revenue

Cost

Profit

Quantity

Discount

Customer

Product

Region

Date

For example, datasets may contain:

sales\_amount

net\_sales

revenue

total\_revenue

The semantic layer can interpret these as variations of the same business concept.

This enables analytics across datasets with different schemas.

Business Intelligence

Once the dataset has been interpreted, EROI generates business analytics automatically.

KPI Intelligence

The platform calculates:

\- Total Revenue

\- Total Profit

\- Profit Margin

\- Total Orders

\- Total Quantity

\- Average Order Value

\- Customer metrics

Revenue Analytics

Analyze revenue across:

\- Time

\- Regions

\- Products

\- Categories

\- Customers

Profitability Analytics

Analyze:

\- Product profitability

\- Profit contribution

\- Profit margins

\- Revenue-to-profit relationships

Regional Analytics

Analyze:

\- Regional revenue

\- Regional profitability

\- Regional contribution

\- Regional performance

Product Analytics

Analyze:

\- Product revenue

\- Product profit

\- Product rankings

\- Product contribution

\- Profitability differences

Discount Analytics

Analyze the relationship between:

\- Discounts

\- Revenue

\- Profit

\- Profit Margin

Single-File Analysis

A single business dataset can be uploaded and analyzed automatically.

Upload File

&#x20;    ↓

Universal Reader

&#x20;    ↓

Data Profiling

&#x20;    ↓

Quality Assessment

&#x20;    ↓

Semantic Detection

&#x20;    ↓

Business KPI Detection

&#x20;    ↓

Revenue Analytics

&#x20;    ↓

Profitability Analytics

&#x20;    ↓

Regional Analytics

&#x20;    ↓

Product Analytics

&#x20;    ↓

Dashboard

Multi-File Business Comparison

EROI supports comparison of multiple business datasets.

The comparison engine evaluates both:

Physical Schema Comparison

Identifies common columns and structural differences.

Semantic Business Comparison

Compares business concepts even when column names differ.

Example:

Dataset A

sales\_amount



Dataset B

net\_revenue



&#x20;       ↓



Semantic Interpretation



&#x20;       ↓



Revenue ↔ Revenue

Business metrics that can be compared include:

\- Revenue

\- Profit

\- Profit Margin

\- Orders

\- Quantity

\- Average Order Value

System Architecture

&#x20;                   ┌─────────────────────────┐

&#x20;                   │       User / Analyst    │

&#x20;                   └────────────┬────────────┘

&#x20;                                │

&#x20;                                ▼

&#x20;                   ┌─────────────────────────┐

&#x20;                   │     Next.js Dashboard   │

&#x20;                   │      React / TypeScript  │

&#x20;                   └────────────┬────────────┘

&#x20;                                │

&#x20;                                ▼

&#x20;                   ┌─────────────────────────┐

&#x20;                   │      API Proxy Layer    │

&#x20;                   └────────────┬────────────┘

&#x20;                                │

&#x20;                                ▼

&#x20;                   ┌─────────────────────────┐

&#x20;                   │       FastAPI API       │

&#x20;                   └────────────┬────────────┘

&#x20;                                │

&#x20;             ┌──────────────────┼──────────────────┐

&#x20;             │                  │                  │

&#x20;             ▼                  ▼                  ▼

&#x20;      ┌─────────────┐   ┌──────────────┐   ┌───────────────┐

&#x20;      │  Ingestion  │   │  Analytics   │   │ Data Quality  │

&#x20;      └──────┬──────┘   └──────┬───────┘   └───────┬───────┘

&#x20;             │                 │                   │

&#x20;             └─────────────────┼───────────────────┘

&#x20;                               ▼

&#x20;                   ┌─────────────────────────┐

&#x20;                   │ Semantic Detection      │

&#x20;                   │ Business Intelligence   │

&#x20;                   └────────────┬────────────┘

&#x20;                                │

&#x20;                   ┌────────────┴────────────┐

&#x20;                   ▼                         ▼

&#x20;         ┌──────────────────┐      ┌──────────────────┐

&#x20;         │ PostgreSQL       │      │ Direct File      │

&#x20;         │ Data Warehouse   │      │ Analysis         │

&#x20;         └──────────────────┘      └──────────────────┘

Data Warehouse Architecture

EROI uses a dimensional warehouse design.

&#x20;                DimDate

&#x20;                   │

&#x20;                   │

DimCustomer ─── FactSales ─── DimProduct

&#x20;                   │

&#x20;                   │

&#x20;               DimRegion

Warehouse components

\- FactSales

\- DimDate

\- DimCustomer

\- DimProduct

\- DimRegion

This structure supports analytical queries across business dimensions.

Technology Stack

Backend

Technology	Purpose

Python	Core application

FastAPI	REST API

Pandas	Data processing

NumPy	Numerical computation

SQLAlchemy	Database interaction

PostgreSQL	Data warehouse

OpenPyXL	Excel processing

PyArrow	Parquet processing

python-docx	DOCX processing

python-pptx	PPTX processing





Frontend

Technology	Purpose

Next.js	Web application

React	User interface

TypeScript	Type-safe frontend

CSS	Dashboard styling





API

Data Ingestion

POST /ingestion/profile

POST /ingestion/profile-multiple

POST /ingestion/compare

Business Analytics

GET /analytics/overview

GET /analytics/regions

GET /analytics/products

GET /analytics/customers/top

Advanced Analytics

GET /analytics/filter-options

GET /analytics/kpis

GET /analytics/monthly

GET /analytics/categories

GET /analytics/regional-performance

GET /analytics/product-profitability

GET /analytics/products/ranking

GET /analytics/discounts

Interactive API Documentation

When the backend is running:

http://127.0.0.1:8000/docs

Project Structure

eroi-platform/

│

├── backend/

│   ├── app/

│   │   ├── analytics/

│   │   │   ├── business\_metrics.py

│   │   │   ├── data\_quality.py

│   │   │   ├── file\_business\_analyzer.py

│   │   │   ├── file\_comparison.py

│   │   │   └── semantic\_detection.py

│   │   │

│   │   ├── api/

│   │   │   ├── analytics.py

│   │   │   ├── advanced\_analytics.py

│   │   │   └── ingestion.py

│   │   │

│   │   ├── core/

│   │   ├── db/

│   │   ├── etl/

│   │   ├── models/

│   │   ├── quality/

│   │   ├── schemas/

│   │   ├── services/

│   │   ├── utils/

│   │   └── main.py

│   │

│   ├── requirements.txt

│   └── .env.example

│

├── frontend/

│   ├── src/

│   │   ├── app/

│   │   │   ├── api/

│   │   │   ├── layout.tsx

│   │   │   ├── page.tsx

│   │   │   └── globals.css

│   │   │

│   │   └── components/

│   │       └── MultiFileAnalysis.tsx

│   │

│   ├── package.json

│   └── tsconfig.json

│

├── data/

│   ├── sales.csv

│   └── sample\_sales.csv

│

├── README.md

└── .gitignore

Quick Start

Prerequisites

\- Python 3.12+

\- Node.js 18+

\- PostgreSQL

\- Git

Backend

cd backend



python -m venv .venv



.\\.venv\\Scripts\\Activate.ps1



pip install -r requirements.txt

Create:

backend/.env

using:

backend/.env.example

Configure the PostgreSQL connection.

Example:

DATABASE\_URL=postgresql://postgres:YOUR\_PASSWORD@127.0.0.1:5433/eroi

Start the API:

python -m uvicorn app.main:app --reload

Backend:

http://127.0.0.1:8000

Swagger:

http://127.0.0.1:8000/docs

Frontend

Open another terminal:

cd frontend



npm install

Create:

frontend/.env.local

with:

EROI\_BACKEND\_URL=http://127.0.0.1:8000

Start:

npm run dev

Open:

http://localhost:3000

Engineering Highlights

EROI demonstrates practical implementation of:

\- Full-stack application architecture

\- REST API development

\- ETL concepts

\- Universal data ingestion

\- Data validation

\- Data quality engineering

\- Semantic schema detection

\- Business KPI computation

\- Analytical data modeling

\- PostgreSQL data warehousing

\- Multi-file business comparison

\- React dashboard development

\- TypeScript

\- Python analytics

\- API/frontend integration

Current Implementation

Completed

\- \[x] Universal file ingestion

\- \[x] Dataset profiling

\- \[x] Data quality analysis

\- \[x] Semantic field detection

\- \[x] KPI analytics

\- \[x] Revenue analytics

\- \[x] Profitability analytics

\- \[x] Regional analytics

\- \[x] Product analytics

\- \[x] Discount analytics

\- \[x] PostgreSQL warehouse

\- \[x] FastAPI backend

\- \[x] Next.js dashboard

\- \[x] Single-file analysis

\- \[x] Multi-file comparison

\- \[x] GitHub repository

Roadmap

Planned enhancements:

\- \[ ] Automated anomaly detection

\- \[ ] Revenue forecasting

\- \[ ] Time-series intelligence

\- \[ ] Natural-language analytics

\- \[ ] AI-generated business insights

\- \[ ] Authentication

\- \[ ] Role-based access control

\- \[ ] Scheduled reports

\- \[ ] Business alerts

\- \[ ] Customer segmentation

\- \[ ] Predictive revenue analytics

\- \[ ] Real-time data pipelines

\- \[ ] Cloud deployment

\- \[ ] Data lineage

\- \[ ] Advanced BI visualizations

Security

Sensitive configuration files are excluded from version control.

The repository does not contain:

\- Database passwords

\- Local environment secrets

\- Frontend local environment variables

\- Virtual environments

\- Node modules

\- Next.js build output

Use the provided .env.example files to configure the application locally.

Author

Karthik Polasi

B.Tech — Electronics \& Communication Engineering

Areas of interest:

\- Data Analytics

\- Business Intelligence

\- Data Engineering

\- Artificial Intelligence

\- Machine Learning

\- Full-Stack Development

\- Intelligent Enterprise Systems

Project

EROI — Enterprise Revenue \& Operations Intelligence Platform

Turning enterprise data into structured operational intelligence.

