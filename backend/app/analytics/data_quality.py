import pandas as pd


def generate_quality_report(df: pd.DataFrame) -> dict:
    """
    Generate a data quality report for an uploaded dataset.
    """

    rows = len(df)
    columns = len(df.columns)

    total_cells = rows * columns

    # Missing values
    missing_by_column = df.isna().sum()

    missing_cells = int(missing_by_column.sum())

    missing_percentage = (
        (missing_cells / total_cells) * 100
        if total_cells > 0
        else 0
    )

    # Duplicate rows
    duplicate_rows = int(df.duplicated().sum())

    duplicate_percentage = (
        (duplicate_rows / rows) * 100
        if rows > 0
        else 0
    )

    # Data types
    data_types = {
        column: str(dtype)
        for column, dtype in df.dtypes.items()
    }

    # Unique values
    unique_values = {
        column: int(df[column].nunique(dropna=True))
        for column in df.columns
    }

    # Quality score
    quality_score = max(
        0,
        100
        - missing_percentage
        - duplicate_percentage
    )

    return {
        "rows": rows,
        "columns": columns,
        "missing_cells": missing_cells,
        "missing_percentage": round(
            missing_percentage,
            2
        ),
        "duplicate_rows": duplicate_rows,
        "duplicate_percentage": round(
            duplicate_percentage,
            2
        ),
        "quality_score": round(
            quality_score,
            2
        ),
        "data_types": data_types,
        "unique_values": unique_values,
        "missing_by_column": {
            column: int(value)
            for column, value
            in missing_by_column.items()
        },
    }