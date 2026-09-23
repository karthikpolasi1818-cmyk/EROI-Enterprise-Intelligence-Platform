"use client";

import {
  ChangeEvent,
  DragEvent,
  useRef,
  useState,
} from "react";

type Props = {
  onAnalysisComplete?: (
    result: any
  ) => void;
};

function formatNumber(value: any) {
  const n = Number(value);

  if (!Number.isFinite(n)) {
    return "-";
  }

  return n.toLocaleString("en-IN", {
    maximumFractionDigits: 2,
  });
}

function formatCurrency(value: any) {
  const n = Number(value);

  if (!Number.isFinite(n)) {
    return "₹0";
  }

  return `₹${n.toLocaleString("en-IN", {
    maximumFractionDigits: 2,
  })}`;
}

export default function MultiFileAnalysis({
  onAnalysisComplete,
}: Props) {
  const inputRef =
    useRef<HTMLInputElement>(null);

  const [files, setFiles] =
    useState<File[]>([]);

  const [results, setResults] =
    useState<any[]>([]);

  const [comparison, setComparison] =
    useState<any>(null);

  const [loading, setLoading] =
    useState(false);

  const [error, setError] =
    useState("");

  const [message, setMessage] =
    useState("");

  const [dragging, setDragging] =
    useState(false);

  const addFiles = (
    selected: File[]
  ) => {
    setFiles((previous) => {
      const existing =
        new Set(
          previous.map(
            (file) => file.name
          )
        );

      return [
        ...previous,
        ...selected.filter(
          (file) =>
            !existing.has(
              file.name
            )
        ),
      ];
    });

    setResults([]);
    setComparison(null);
    setError("");
    setMessage("");
  };

  const handleChange = (
    event: ChangeEvent<HTMLInputElement>
  ) => {
    addFiles(
      Array.from(
        event.target.files || []
      )
    );

    event.target.value = "";
  };

  const handleDrop = (
    event: DragEvent<HTMLDivElement>
  ) => {
    event.preventDefault();

    setDragging(false);

    addFiles(
      Array.from(
        event.dataTransfer.files
      )
    );
  };

  const removeFile = (
    index: number
  ) => {
    setFiles((previous) =>
      previous.filter(
        (_, i) => i !== index
      )
    );

    setResults([]);
    setComparison(null);
  };

  const clearAll = () => {
    setFiles([]);
    setResults([]);
    setComparison(null);
    setError("");
    setMessage("");
  };

  const analyze = async () => {
    if (!files.length) {
      setError(
        "Please select at least one file."
      );
      return;
    }

    setLoading(true);
    setError("");
    setMessage("");
    setResults([]);
    setComparison(null);

    try {
      // ======================================================
      // ONE FILE
      // ======================================================

      if (files.length === 1) {
        const formData =
          new FormData();

        formData.append(
          "file",
          files[0]
        );

        const response =
          await fetch(
            "/api/eroi/ingestion/profile",
            {
              method: "POST",
              body: formData,
              cache: "no-store",
            }
          );

        const data =
          await response.json();

        if (!response.ok || !data.success) {
          throw new Error(
            data?.error ||
              data?.detail ||
              "File analysis failed."
          );
        }

        setResults([data]);

        setMessage(
          `Successfully analyzed ${files[0].name}`
        );

        onAnalysisComplete?.({
          mode: "single",

          sourceName:
            files[0].name,

          kpis:
            data.business_analysis
              ?.kpis || {},

          monthly:
            data.business_analysis
              ?.monthly || [],

          regional:
            data.business_analysis
              ?.regional || [],

          profitability:
            data.business_analysis
              ?.profitability || [],

          ranking:
            data.business_analysis
              ?.ranking || [],

          categories:
            data.business_analysis
              ?.categories || [],

          discounts:
            data.business_analysis
              ?.discounts || [],

          quality:
            data.quality || {},

          semantic:
            data.business_analysis
              ?.semantic_fields || {},

          file: data,
        });

        return;
      }

      // ======================================================
      // MULTIPLE FILES
      // ======================================================

      const formData =
        new FormData();

      files.forEach((file) => {
        formData.append(
          "files",
          file
        );
      });

      const response =
        await fetch(
          "/api/eroi/ingestion/compare",
          {
            method: "POST",
            body: formData,
            cache: "no-store",
          }
        );

      const data =
        await response.json();

      if (!response.ok || !data.success) {
        throw new Error(
          data?.error ||
            data?.detail ||
            "Comparison failed."
        );
      }

      setResults(
        data.files || []
      );

      setComparison(
        data.comparison || null
      );

      setMessage(
        `Successfully compared ${files.length} files.`
      );

      onAnalysisComplete?.({
        mode: "comparison",

        sourceName:
          `${files.length} files`,

        comparison:
          data.comparison || {},

        files:
          data.files || [],
      });
    } catch (err: any) {
      console.error(err);

      setError(
        err?.message ||
          "Unable to analyze files."
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <section
      style={{
        marginTop: 30,
        background: "#ffffff",
        border:
          "1px solid #e2e8f0",
        borderRadius: 20,
        padding: 26,
        boxShadow:
          "0 6px 20px rgba(15,23,42,0.04)",
      }}
    >
      <h2
        style={{
          margin: 0,
          fontSize: 25,
          fontWeight: 850,
          color: "#0f172a",
        }}
      >
        Multi-File Data Intelligence
      </h2>

      <p
        style={{
          color: "#64748b",
          marginTop: 7,
        }}
      >
        Analyze one business file
        individually or compare
        multiple files automatically.
      </p>

      {/* ================================================== */}
      {/* DROP ZONE */}
      {/* ================================================== */}

      <div
        onClick={() =>
          inputRef.current?.click()
        }
        onDragOver={(event) => {
          event.preventDefault();
          setDragging(true);
        }}
        onDragLeave={() =>
          setDragging(false)
        }
        onDrop={handleDrop}
        style={{
          marginTop: 20,
          minHeight: 210,
          border: dragging
            ? "2px solid #2563eb"
            : "2px dashed #cbd5e1",
          borderRadius: 16,
          background: dragging
            ? "#eff6ff"
            : "#f8fafc",
          display: "flex",
          flexDirection: "column",
          justifyContent: "center",
          alignItems: "center",
          cursor: "pointer",
        }}
      >
        <div
          style={{
            fontSize: 42,
          }}
        >
          📊
        </div>

        <h3
          style={{
            margin:
              "10px 0 5px",
            color: "#0f172a",
          }}
        >
          Upload business data
        </h3>

        <p
          style={{
            color: "#64748b",
            textAlign: "center",
          }}
        >
          One file → individual
          analysis
          <br />
          Multiple files → cross-file
          comparison
        </p>

        <button
          type="button"
          onClick={(event) => {
            event.stopPropagation();

            inputRef.current?.click();
          }}
          style={{
            border: 0,
            background: "#2563eb",
            color: "#ffffff",
            padding:
              "12px 22px",
            borderRadius: 9,
            fontWeight: 800,
            cursor: "pointer",
          }}
        >
          Choose Files
        </button>

        <input
          ref={inputRef}
          type="file"
          hidden
          multiple
          accept=".csv,.xlsx,.xls,.json,.parquet,.pdf,.docx,.pptx,.txt,.md,.log,.xml,.html"
          onChange={handleChange}
        />
      </div>

      {/* ================================================== */}
      {/* MESSAGES */}
      {/* ================================================== */}

      {error && (
        <div
          style={{
            marginTop: 15,
            padding: 14,
            borderRadius: 10,
            background: "#fef2f2",
            color: "#991b1b",
            border:
              "1px solid #fecaca",
            fontWeight: 700,
          }}
        >
          {error}
        </div>
      )}

      {message && (
        <div
          style={{
            marginTop: 15,
            padding: 14,
            borderRadius: 10,
            background: "#f0fdf4",
            color: "#166534",
            border:
              "1px solid #bbf7d0",
            fontWeight: 700,
          }}
        >
          {message}
        </div>
      )}

      {/* ================================================== */}
      {/* SELECTED FILES */}
      {/* ================================================== */}

      {files.length > 0 && (
        <div
          style={{
            marginTop: 24,
          }}
        >
          <div
            style={{
              display: "flex",
              justifyContent:
                "space-between",
              alignItems: "center",
            }}
          >
            <h3
              style={{
                margin: 0,
                color: "#0f172a",
              }}
            >
              Selected Files (
              {files.length})
            </h3>

            <button
              type="button"
              onClick={clearAll}
              style={{
                border: 0,
                background:
                  "transparent",
                color: "#dc2626",
                fontWeight: 800,
                cursor: "pointer",
              }}
            >
              Clear All
            </button>
          </div>

          <div
            style={{
              marginTop: 12,
            }}
          >
            {files.map(
              (
                file,
                index
              ) => (
                <div
                  key={`${file.name}-${index}`}
                  style={{
                    display: "flex",
                    justifyContent:
                      "space-between",
                    alignItems:
                      "center",
                    padding: 14,
                    border:
                      "1px solid #e2e8f0",
                    borderRadius: 10,
                    marginBottom: 8,
                  }}
                >
                  <div>
                    <strong>
                      {file.name}
                    </strong>

                    <div
                      style={{
                        fontSize: 12,
                        color:
                          "#64748b",
                        marginTop: 4,
                      }}
                    >
                      {(
                        file.size /
                        1024
                      ).toFixed(
                        2
                      )}{" "}
                      KB
                    </div>
                  </div>

                  <button
                    type="button"
                    onClick={() =>
                      removeFile(
                        index
                      )
                    }
                    style={{
                      border:
                        "1px solid #fecaca",
                      background:
                        "#fff1f2",
                      color:
                        "#be123c",
                      padding:
                        "8px 14px",
                      borderRadius: 8,
                      cursor:
                        "pointer",
                      fontWeight: 700,
                    }}
                  >
                    Remove
                  </button>
                </div>
              )
            )}
          </div>

          <button
            type="button"
            disabled={loading}
            onClick={analyze}
            style={{
              marginTop: 10,
              border: 0,
              background: loading
                ? "#94a3b8"
                : "#2563eb",
              color: "#ffffff",
              padding:
                "13px 24px",
              borderRadius: 9,
              fontWeight: 800,
              cursor: loading
                ? "not-allowed"
                : "pointer",
            }}
          >
            {loading
              ? "Analyzing..."
              : files.length === 1
              ? "Analyze File"
              : `Compare ${files.length} Files`}
          </button>
        </div>
      )}

      {/* ================================================== */}
      {/* FILE RESULT TABLE */}
      {/* ================================================== */}

      {results.length > 0 && (
        <div
          style={{
            marginTop: 30,
          }}
        >
          <h3>
            {results.length === 1
              ? "File Analysis Result"
              : "Files Being Compared"}
          </h3>

          <div
            style={{
              overflowX:
                "auto",
              border:
                "1px solid #e2e8f0",
              borderRadius: 12,
            }}
          >
            <table
              style={{
                width: "100%",
                borderCollapse:
                  "collapse",
                minWidth: 900,
              }}
            >
              <thead>
                <tr
                  style={{
                    background:
                      "#f8fafc",
                  }}
                >
                  {[
                    "File",
                    "Type",
                    "Rows",
                    "Columns",
                    "Quality",
                    "Revenue",
                    "Profit",
                    "Orders",
                  ].map(
                    (column) => (
                      <th
                        key={column}
                        style={
                          thStyle
                        }
                      >
                        {column}
                      </th>
                    )
                  )}
                </tr>
              </thead>

              <tbody>
                {results.map(
                  (
                    result,
                    index
                  ) => {
                    const analysis =
                      result.business_analysis ||
                      {};

                    const kpis =
                      analysis.kpis ||
                      {};

                    return (
                      <tr
                        key={
                          index
                        }
                      >
                        <td
                          style={
                            tdStyle
                          }
                        >
                          <strong>
                            {
                              result.filename
                            }
                          </strong>
                        </td>

                        <td
                          style={
                            tdStyle
                          }
                        >
                          {
                            result.file_type
                          }
                        </td>

                        <td
                          style={
                            tdStyle
                          }
                        >
                          {formatNumber(
                            result
                              .dataset
                              ?.rows ??
                              result.rows
                          )}
                        </td>

                        <td
                          style={
                            tdStyle
                          }
                        >
                          {formatNumber(
                            result
                              .dataset
                              ?.columns ??
                              result.columns
                          )}
                        </td>

                        <td
                          style={
                            tdStyle
                          }
                        >
                          {formatNumber(
                            result
                              .quality
                              ?.score
                          )}
                        </td>

                        <td
                          style={
                            tdStyle
                          }
                        >
                          {formatCurrency(
                            kpis.total_revenue
                          )}
                        </td>

                        <td
                          style={
                            tdStyle
                          }
                        >
                          {formatCurrency(
                            kpis.total_profit
                          )}
                        </td>

                        <td
                          style={
                            tdStyle
                          }
                        >
                          {formatNumber(
                            kpis.total_orders
                          )}
                        </td>
                      </tr>
                    );
                  }
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* ================================================== */}
      {/* SEMANTIC COMPARISON */}
      {/* ================================================== */}

      {comparison && (
        <div
          style={{
            marginTop: 30,
          }}
        >
          <h3
            style={{
              color: "#0f172a",
            }}
          >
            Cross-File Comparison
          </h3>

          <p
            style={{
              color: "#64748b",
            }}
          >
            EROI compares business
            meaning even when the
            physical column names differ.
          </p>

          <div
            style={{
              display: "grid",
              gridTemplateColumns:
                "repeat(auto-fit,minmax(200px,1fr))",
              gap: 12,
              marginTop: 15,
            }}
          >
            {[
              [
                "Common Business Fields",
                comparison
                  .common_business_fields
                  ?.join(", ") ||
                  "None",
              ],
              [
                "Physical Common Columns",
                comparison
                  .common_columns
                  ?.join(", ") ||
                  "None",
              ],
            ].map(
              ([title, value]) => (
                <div
                  key={title}
                  style={{
                    padding: 16,
                    background:
                      "#f8fafc",
                    border:
                      "1px solid #e2e8f0",
                    borderRadius: 12,
                  }}
                >
                  <div
                    style={{
                      fontSize: 12,
                      color:
                        "#64748b",
                      fontWeight: 800,
                    }}
                  >
                    {title}
                  </div>

                  <div
                    style={{
                      marginTop: 7,
                      color:
                        "#0f172a",
                      fontWeight: 700,
                      wordBreak:
                        "break-word",
                    }}
                  >
                    {value}
                  </div>
                </div>
              )
            )}
          </div>

          <div
            style={{
              marginTop: 20,
            }}
          >
            {comparison.metric_comparison?.map(
              (metric: any) => (
                <div
                  key={
                    metric.key
                  }
                  style={{
                    marginBottom: 14,
                    padding: 17,
                    border:
                      "1px solid #e2e8f0",
                    borderRadius: 12,
                  }}
                >
                  <strong>
                    {metric.metric}
                  </strong>

                  <div
                    style={{
                      display:
                        "grid",
                      gridTemplateColumns:
                        "repeat(auto-fit,minmax(210px,1fr))",
                      gap: 10,
                      marginTop: 12,
                    }}
                  >
                    {metric.values?.map(
                      (
                        item: any,
                        index: number
                      ) => (
                        <div
                          key={
                            item.filename
                          }
                          style={{
                            padding: 14,
                            background:
                              "#f8fafc",
                            borderRadius:
                              9,
                          }}
                        >
                          <div
                            style={{
                              fontSize:
                                12,
                              color:
                                "#64748b",
                            }}
                          >
                            {
                              item.filename
                            }
                          </div>

                          <div
                            style={{
                              marginTop:
                                5,
                              fontSize:
                                20,
                              fontWeight:
                                850,
                              color:
                                "#0f172a",
                            }}
                          >
                            {metric.key ===
                              "total_revenue" ||
                            metric.key ===
                              "total_profit" ||
                            metric.key ===
                              "aov"
                              ? formatCurrency(
                                  item.value
                                )
                              : metric.key ===
                                "profit_margin"
                              ? `${formatNumber(
                                  item.value
                                )}%`
                              : formatNumber(
                                  item.value
                                )}
                          </div>

                          {index >
                            0 && (
                            <div
                              style={{
                                marginTop:
                                  5,
                                fontSize:
                                  12,
                                fontWeight:
                                  700,
                                color:
                                  item.change >=
                                  0
                                    ? "#15803d"
                                    : "#dc2626",
                              }}
                            >
                              {item.change >=
                              0
                                ? "+"
                                : ""}
                              {formatNumber(
                                item.change
                              )}{" "}
                              (
                              {item.change_percent >=
                              0
                                ? "+"
                                : ""}
                              {formatNumber(
                                item.change_percent
                              )}
                              %)
                            </div>
                          )}
                        </div>
                      )
                    )}
                  </div>
                </div>
              )
            )}
          </div>
        </div>
      )}
    </section>
  );
}

const thStyle: React.CSSProperties = {
  textAlign: "left",
  padding: 13,
  fontSize: 12,
  color: "#475569",
  borderBottom:
    "1px solid #e2e8f0",
  whiteSpace: "nowrap",
};

const tdStyle: React.CSSProperties = {
  padding: 13,
  fontSize: 13,
  color: "#334155",
  borderBottom:
    "1px solid #f1f5f9",
  whiteSpace: "nowrap",
};