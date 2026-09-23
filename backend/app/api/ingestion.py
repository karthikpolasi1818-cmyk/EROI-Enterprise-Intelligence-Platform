from __future__ import annotations

import pandas as pd
from fastapi import APIRouter, File, UploadFile

from app.services.universal_reader import (
    read_uploaded_file,
    detect_file_type,
)

from app.analytics.file_business_analyzer import (
    analyze_dataframe,
    calculate_file_quality,
    compare_business_results,
)


router = APIRouter(
    prefix="/ingestion",
    tags=["Data Ingestion"],
)


# ============================================================
# READ UPLOADED FILE
# ============================================================

async def read_file(
    file: UploadFile,
):
    contents = await file.read()

    if not contents:
        raise ValueError(
            f"{file.filename}: file is empty."
        )

    parsed = read_uploaded_file(
        file.filename or "unknown",
        contents,
    )

    return parsed


# ============================================================
# SINGLE FILE PROFILE
# ============================================================

@router.post("/profile")
async def profile_file(
    file: UploadFile = File(...),
):

    try:

        filename = (
            file.filename
            or "unknown"
        )

        parsed = await read_file(
            file
        )

        file_type = detect_file_type(
            filename
        )

        # ----------------------------------------------------
        # DATASET
        # ----------------------------------------------------

        if isinstance(
            parsed,
            pd.DataFrame,
        ):

            analysis = analyze_dataframe(
                parsed
            )

            return {
                "success": True,
                "mode": "single",
                "filename": filename,
                "file_type": file_type,
                "kind": "dataset",

                "dataset": {
                    "rows": len(parsed),
                    "columns": len(
                        parsed.columns
                    ),
                    "column_names": [
                        str(column)
                        for column in parsed.columns
                    ],
                },

                "quality": analysis[
                    "quality"
                ],

                "business_analysis": analysis,

                # Backward compatibility
                "rows": len(parsed),
                "columns": len(
                    parsed.columns
                ),
                "quality_score": analysis[
                    "quality"
                ]["score"],
                "missing_cells": analysis[
                    "quality"
                ]["missing_cells"],
                "duplicate_rows": analysis[
                    "quality"
                ]["duplicate_rows"],
            }

        # ----------------------------------------------------
        # DOCUMENT
        # ----------------------------------------------------

        if isinstance(
            parsed,
            dict,
        ):

            return {
                "success": True,
                "mode": "single",
                "filename": filename,
                "file_type": file_type,
                "kind": "document",
                "document": parsed,
                "business_analysis": {
                    "quality": {},
                    "kpis": {},
                    "monthly": [],
                    "regional": [],
                    "profitability": [],
                    "ranking": [],
                    "categories": [],
                    "discounts": [],
                    "semantic_fields": {},
                    "available_semantics": [],
                },
            }

        raise ValueError(
            "Unsupported parsed file result."
        )

    except Exception as exc:

        return {
            "success": False,
            "mode": "single",
            "filename": (
                file.filename
                or "unknown"
            ),
            "error": str(exc),
        }


# ============================================================
# MULTIPLE FILE PROFILE
# ============================================================

@router.post("/profile-multiple")
async def profile_multiple_files(
    files: list[UploadFile] = File(...),
):

    results = []

    for file in files:

        result = await profile_file(
            file
        )

        results.append(result)

    return {
        "success": True,
        "mode": "multiple",
        "total_files": len(files),
        "results": results,
    }


# ============================================================
# MULTI FILE COMPARISON
# ============================================================

@router.post("/compare")
async def compare_files(
    files: list[UploadFile] = File(...),
):

    if len(files) < 2:

        return {
            "success": False,
            "mode": "comparison",
            "error": (
                "Comparison requires at least 2 files."
            ),
        }

    results = []

    physical_column_sets = []

    all_columns = set()

    datasets = 0
    documents = 0

    # ========================================================
    # ANALYZE EACH FILE
    # ========================================================

    for file in files:

        try:

            filename = (
                file.filename
                or "unknown"
            )

            parsed = await read_file(
                file
            )

            file_type = detect_file_type(
                filename
            )

            # ------------------------------------------------
            # DATASET
            # ------------------------------------------------

            if isinstance(
                parsed,
                pd.DataFrame,
            ):

                datasets += 1

                columns = [
                    str(column)
                    for column
                    in parsed.columns
                ]

                all_columns.update(
                    columns
                )

                physical_column_sets.append(
                    set(
                        column.lower()
                        for column
                        in columns
                    )
                )

                analysis = analyze_dataframe(
                    parsed
                )

                results.append(
                    {
                        "success": True,
                        "filename": filename,
                        "file_type": file_type,
                        "kind": "dataset",

                        "dataset": {
                            "rows": len(parsed),
                            "columns": len(
                                parsed.columns
                            ),
                            "column_names": columns,
                        },

                        "quality": analysis[
                            "quality"
                        ],

                        "business_analysis": analysis,

                        "rows": len(parsed),
                        "columns": len(
                            parsed.columns
                        ),
                        "quality_score": analysis[
                            "quality"
                        ]["score"],
                        "missing_cells": analysis[
                            "quality"
                        ]["missing_cells"],
                        "duplicate_rows": analysis[
                            "quality"
                        ]["duplicate_rows"],
                    }
                )

            # ------------------------------------------------
            # DOCUMENT
            # ------------------------------------------------

            elif isinstance(
                parsed,
                dict,
            ):

                documents += 1

                results.append(
                    {
                        "success": True,
                        "filename": filename,
                        "file_type": file_type,
                        "kind": "document",
                        "document": parsed,

                        "business_analysis": {
                            "quality": {},
                            "kpis": {},
                            "monthly": [],
                            "regional": [],
                            "profitability": [],
                            "ranking": [],
                            "categories": [],
                            "discounts": [],
                            "semantic_fields": {},
                            "available_semantics": [],
                        },
                    }
                )

            else:

                results.append(
                    {
                        "success": False,
                        "filename": filename,
                        "error": (
                            "Unsupported file."
                        ),
                    }
                )

        except Exception as exc:

            results.append(
                {
                    "success": False,
                    "filename": (
                        file.filename
                        or "unknown"
                    ),
                    "error": str(exc),
                }
            )

    # ========================================================
    # PHYSICAL COLUMN COMPARISON
    # ========================================================

    if physical_column_sets:

        common_columns = sorted(
            list(
                set.intersection(
                    *physical_column_sets
                )
            )
        )

    else:

        common_columns = []

    # ========================================================
    # SEMANTIC BUSINESS COMPARISON
    # ========================================================

    successful_datasets = [
        item
        for item in results
        if (
            item.get("success")
            and item.get("kind")
            == "dataset"
        )
    ]

    business_comparison = (
        compare_business_results(
            successful_datasets
        )
        if successful_datasets
        else {
            "semantic_comparison": False,
            "metric_comparison": [],
            "common_business_fields": [],
            "all_business_fields": [],
        }
    )

    # ========================================================
    # FINAL RESPONSE
    # ========================================================

    return {
        "success": True,
        "mode": "comparison",

        "summary": {
            "total_files": len(files),
            "datasets": datasets,
            "documents": documents,
        },

        "comparison": {
            "common_columns": common_columns,
            "all_columns": sorted(
                list(all_columns)
            ),

            **business_comparison,
        },

        "files": results,

        "individual_results": results,
    }