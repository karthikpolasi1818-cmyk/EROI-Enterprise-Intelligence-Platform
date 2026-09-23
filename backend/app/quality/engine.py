from __future__ import annotations

import pandas as pd


def calculate_quality_score(df: pd.DataFrame) -> dict:

    rows = len(df)
    columns = len(df.columns)

    if rows == 0:
        return {
            "score": 0,
            "status": "EMPTY",
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

    return {
        "score": round(score, 2),
        "status": (
            "EXCELLENT"
            if score >= 95
            else "GOOD"
            if score >= 85
            else "WARNING"
            if score >= 70
            else "CRITICAL"
        ),
        "rows": rows,
        "columns": columns,
        "missing_cells": missing_cells,
        "missing_rate": round(
            missing_rate,
            2,
        ),
        "duplicate_rows": duplicate_rows,
        "duplicate_rate": round(
            duplicate_rate,
            2,
        ),
    }


def detect_quality_issues(
    df: pd.DataFrame,
) -> list[dict]:

    issues = []

    for column in df.columns:

        missing = int(
            df[column].isna().sum()
        )

        if missing > 0:
            issues.append(
                {
                    "type": "MISSING_VALUES",
                    "column": str(column),
                    "count": missing,
                }
            )

    for column in df.select_dtypes(
        include="number"
    ).columns:

        series = df[column].dropna()

        if len(series) < 4:
            continue

        q1 = series.quantile(0.25)
        q3 = series.quantile(0.75)

        iqr = q3 - q1

        lower = q1 - 1.5 * iqr
        upper = q3 + 1.5 * iqr

        outliers = int(
            ((series < lower) | (series > upper)).sum()
        )

        if outliers > 0:
            issues.append(
                {
                    "type": "OUTLIERS",
                    "column": str(column),
                    "count": outliers,
                }
            )

    return issues