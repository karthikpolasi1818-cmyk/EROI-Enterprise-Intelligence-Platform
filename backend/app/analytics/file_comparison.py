from __future__ import annotations

from itertools import combinations
from typing import Any

import pandas as pd


def _clean_column_names(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    df.columns = [
        str(column).strip()
        for column in df.columns
    ]

    return df


def _quality_report(df: pd.DataFrame) -> dict[str, Any]:
    rows = len(df)
    columns = len(df.columns)

    total_cells = rows * columns

    missing_cells = int(df.isna().sum().sum())

    duplicate_rows = int(
        df.duplicated().sum()
    )

    missing_percentage = (
        missing_cells / total_cells * 100
        if total_cells
        else 0
    )

    duplicate_percentage = (
        duplicate_rows / rows * 100
        if rows
        else 0
    )

    return {
        "rows": rows,
        "columns": columns,
        "missing_cells": missing_cells,
        "missing_percentage": round(
            missing_percentage,
            2,
        ),
        "duplicate_rows": duplicate_rows,
        "duplicate_percentage": round(
            duplicate_percentage,
            2,
        ),
        "quality_score": round(
            max(
                0,
                100
                - missing_percentage
                - duplicate_percentage,
            ),
            2,
        ),
    }


def _numeric_summary(
    df: pd.DataFrame,
) -> dict[str, dict[str, float]]:
    result = {}

    numeric_columns = df.select_dtypes(
        include="number"
    ).columns

    for column in numeric_columns:
        series = pd.to_numeric(
            df[column],
            errors="coerce",
        )

        result[column] = {
            "sum": round(
                float(series.sum()),
                2,
            ),
            "average": round(
                float(series.mean()),
                2,
            )
            if not series.dropna().empty
            else 0,
            "minimum": round(
                float(series.min()),
                2,
            )
            if not series.dropna().empty
            else 0,
            "maximum": round(
                float(series.max()),
                2,
            )
            if not series.dropna().empty
            else 0,
        }

    return result


def profile_file(
    filename: str,
    df: pd.DataFrame,
) -> dict[str, Any]:
    df = _clean_column_names(df)

    quality = _quality_report(df)

    return {
        "filename": filename,
        "rows": len(df),
        "columns": len(df.columns),
        "column_names": list(df.columns),
        "data_types": {
            column: str(dtype)
            for column, dtype in df.dtypes.items()
        },
        "quality": quality,
        "numeric_summary": _numeric_summary(df),
    }


def compare_schema(
    datasets: dict[str, pd.DataFrame],
) -> dict[str, Any]:
    column_sets = {
        filename: set(df.columns)
        for filename, df in datasets.items()
    }

    all_columns = set()

    for columns in column_sets.values():
        all_columns.update(columns)

    common_columns = (
        set.intersection(*column_sets.values())
        if column_sets
        else set()
    )

    unique_columns = {}

    for filename, columns in column_sets.items():
        unique_columns[filename] = sorted(
            columns - common_columns
        )

    return {
        "all_columns": sorted(all_columns),
        "common_columns": sorted(
            common_columns
        ),
        "unique_columns_by_file": unique_columns,
    }


def _compare_numeric_columns(
    df_a: pd.DataFrame,
    df_b: pd.DataFrame,
    common_columns: list[str],
) -> dict[str, Any]:
    numeric_comparison = {}

    for column in common_columns:
        if not (
            pd.api.types.is_numeric_dtype(
                df_a[column]
            )
            and pd.api.types.is_numeric_dtype(
                df_b[column]
            )
        ):
            continue

        a_sum = float(
            pd.to_numeric(
                df_a[column],
                errors="coerce",
            ).sum()
        )

        b_sum = float(
            pd.to_numeric(
                df_b[column],
                errors="coerce",
            ).sum()
        )

        difference = b_sum - a_sum

        percentage_change = (
            difference / a_sum * 100
            if a_sum
            else None
        )

        numeric_comparison[column] = {
            "file_a_sum": round(a_sum, 2),
            "file_b_sum": round(b_sum, 2),
            "difference": round(
                difference,
                2,
            ),
            "percentage_change": round(
                percentage_change,
                2,
            )
            if percentage_change is not None
            else None,
        }

    return numeric_comparison


def compare_pair(
    filename_a: str,
    df_a: pd.DataFrame,
    filename_b: str,
    df_b: pd.DataFrame,
) -> dict[str, Any]:
    columns_a = set(df_a.columns)
    columns_b = set(df_b.columns)

    common_columns = sorted(
        columns_a & columns_b
    )

    numeric_comparison = _compare_numeric_columns(
        df_a,
        df_b,
        common_columns,
    )

    return {
        "file_a": filename_a,
        "file_b": filename_b,
        "file_a_rows": len(df_a),
        "file_b_rows": len(df_b),
        "common_columns": common_columns,
        "columns_only_in_file_a": sorted(
            columns_a - columns_b
        ),
        "columns_only_in_file_b": sorted(
            columns_b - columns_a
        ),
        "numeric_comparison": numeric_comparison,
    }


def compare_datasets(
    datasets: dict[str, pd.DataFrame],
) -> dict[str, Any]:
    filenames = list(datasets.keys())

    profiles = [
        profile_file(
            filename,
            datasets[filename],
        )
        for filename in filenames
    ]

    schema = compare_schema(
        datasets
    )

    pairwise_comparisons = []

    for (
        filename_a,
        filename_b,
    ) in combinations(filenames, 2):
        pairwise_comparisons.append(
            compare_pair(
                filename_a,
                datasets[filename_a],
                filename_b,
                datasets[filename_b],
            )
        )

    return {
        "file_count": len(filenames),
        "files": profiles,
        "schema_comparison": schema,
        "pairwise_comparisons": pairwise_comparisons,
    }