"use client";

import {
  useCallback,
  useEffect,
  useState,
} from "react";

import MultiFileAnalysis from "../components/MultiFileAnalysis";


type DashboardMode =
  | "warehouse"
  | "single"
  | "comparison";


type DashboardData = {
  mode: DashboardMode;

  sourceName?: string;

  kpis: any;

  monthly: any[];

  regional: any[];

  profitability: any[];

  ranking: any[];

  categories: any[];

  discounts: any[];

  quality?: any;

  semantic?: any;

  comparison?: any;

  files?: any[];
};


type ApiData =
  Record<string, any>;


// ============================================================
// API
// ============================================================

async function apiFetch<T = ApiData>(
  endpoint: string
): Promise<T> {

  const response =
    await fetch(
      `/api/eroi${endpoint}`,
      {
        method: "GET",
        cache: "no-store",
        headers: {
          Accept:
            "application/json",
        },
      }
    );

  if (!response.ok) {

    const text =
      await response.text();

    throw new Error(
      `EROI API ${response.status}: ${
        text ||
        response.statusText
      }`
    );
  }

  return response.json();
}


// ============================================================
// HELPERS
// ============================================================

function numberValue(
  value: any
): number {

  const numeric =
    Number(value);

  return Number.isFinite(
    numeric
  )
    ? numeric
    : 0;
}


function formatNumber(
  value: any
): string {

  return numberValue(
    value
  ).toLocaleString(
    "en-IN",
    {
      maximumFractionDigits: 2,
    }
  );
}


function formatCurrency(
  value: any
): string {

  return `₹${numberValue(
    value
  ).toLocaleString(
    "en-IN",
    {
      maximumFractionDigits: 0,
    }
  )}`;
}


function formatPercent(
  value: any
): string {

  return `${numberValue(
    value
  ).toLocaleString(
    "en-IN",
    {
      maximumFractionDigits: 2,
    }
  )}%`;
}


function extractArray(
  data: any,
  keys: string[] = []
): any[] {

  if (
    Array.isArray(data)
  ) {
    return data;
  }

  if (
    !data ||
    typeof data !==
      "object"
  ) {
    return [];
  }

  for (
    const key of keys
  ) {

    if (
      Array.isArray(
        data[key]
      )
    ) {
      return data[key];
    }
  }

  for (
    const value of Object.values(
      data
    )
  ) {

    if (
      Array.isArray(value)
    ) {
      return value;
    }
  }

  return [];
}


function getMetric(
  object: any,
  keys: string[],
  fallback = 0
): number {

  if (!object) {
    return fallback;
  }

  for (
    const key of keys
  ) {

    if (
      object[key] !==
        undefined &&
      object[key] !== null
    ) {

      return numberValue(
        object[key]
      );
    }
  }

  return fallback;
}


// ============================================================
// CARD
// ============================================================

function Card({
  title,
  value,
  subtitle,
}: {
  title: string;
  value: string;
  subtitle?: string;
}) {

  return (
    <div
      style={{
        background:
          "#ffffff",
        border:
          "1px solid #e2e8f0",
        borderRadius: 16,
        padding: 20,
        boxShadow:
          "0 6px 20px rgba(15,23,42,0.05)",
      }}
    >

      <div
        style={{
          fontSize: 13,
          fontWeight: 700,
          color:
            "#64748b",
          textTransform:
            "uppercase",
          letterSpacing:
            "0.04em",
        }}
      >
        {title}
      </div>

      <div
        style={{
          marginTop: 8,
          fontSize: 28,
          fontWeight: 850,
          color:
            "#0f172a",
          wordBreak:
            "break-word",
        }}
      >
        {value}
      </div>

      {subtitle && (
        <div
          style={{
            marginTop: 6,
            fontSize: 12,
            color:
              "#94a3b8",
          }}
        >
          {subtitle}
        </div>
      )}

    </div>
  );
}


// ============================================================
// SECTION
// ============================================================

function Section({
  title,
  subtitle,
  children,
}: {
  title: string;
  subtitle?: string;
  children: React.ReactNode;
}) {

  return (
    <section
      style={{
        marginTop: 28,
        background:
          "#ffffff",
        border:
          "1px solid #e2e8f0",
        borderRadius: 18,
        padding: 22,
        boxShadow:
          "0 6px 20px rgba(15,23,42,0.04)",
      }}
    >

      <div
        style={{
          marginBottom: 18,
        }}
      >

        <h2
          style={{
            margin: 0,
            fontSize: 20,
            fontWeight: 850,
            color:
              "#0f172a",
          }}
        >
          {title}
        </h2>

        {subtitle && (
          <p
            style={{
              margin:
                "6px 0 0",
              color:
                "#64748b",
              fontSize: 13,
            }}
          >
            {subtitle}
          </p>
        )}

      </div>

      {children}

    </section>
  );
}


// ============================================================
// DATA TABLE
// ============================================================

function DataTable({
  columns,
  rows,
}: {
  columns: string[];
  rows: any[];
}) {

  if (!rows.length) {

    return (
      <div
        style={{
          padding: 20,
          borderRadius: 12,
          background:
            "#f8fafc",
          color:
            "#64748b",
        }}
      >
        No data available
        for this section.
      </div>
    );
  }

  return (
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
          minWidth: 650,
        }}
      >

        <thead>

          <tr
            style={{
              background:
                "#f8fafc",
            }}
          >

            {columns.map(
              (column) => (
                <th
                  key={
                    column
                  }
                  style={{
                    textAlign:
                      "left",
                    padding: 13,
                    fontSize: 12,
                    color:
                      "#475569",
                    borderBottom:
                      "1px solid #e2e8f0",
                    whiteSpace:
                      "nowrap",
                  }}
                >
                  {column}
                </th>
              )
            )}

          </tr>

        </thead>

        <tbody>

          {rows
            .slice(0, 20)
            .map(
              (
                row,
                rowIndex
              ) => (

                <tr
                  key={
                    rowIndex
                  }
                >

                  {columns.map(
                    (column) => {

                      const value =
                        row?.[
                          column
                        ];

                      return (
                        <td
                          key={
                            column
                          }
                          style={{
                            padding: 13,
                            fontSize: 13,
                            color:
                              "#334155",
                            borderBottom:
                              "1px solid #f1f5f9",
                            whiteSpace:
                              "nowrap",
                          }}
                        >
                          {typeof value ===
                          "number"
                            ? formatNumber(
                                value
                              )
                            : String(
                                value ??
                                  "-"
                              )}
                        </td>
                      );
                    }
                  )}

                </tr>
              )
            )}

        </tbody>

      </table>

    </div>
  );
}


// ============================================================
// STANDARD DASHBOARD
// ============================================================

function Dashboard({
  data,
}: {
  data: DashboardData;
}) {

  const kpis =
    data.kpis || {};

  const revenue =
    getMetric(
      kpis,
      [
        "total_revenue",
        "revenue",
        "sales",
        "total_sales",
      ]
    );

  const profit =
    getMetric(
      kpis,
      [
        "total_profit",
        "profit",
        "net_profit",
        "gross_profit",
      ]
    );

  const margin =
    getMetric(
      kpis,
      [
        "profit_margin",
        "margin",
        "profitMargin",
      ],
      revenue
        ? (profit /
            revenue) *
          100
        : 0
    );

  const orders =
    getMetric(
      kpis,
      [
        "total_orders",
        "orders",
        "order_count",
        "transactions",
      ]
    );

  const quantity =
    getMetric(
      kpis,
      [
        "total_quantity",
        "quantity",
        "units",
        "total_units",
      ]
    );

  const aov =
    getMetric(
      kpis,
      [
        "aov",
        "average_order_value",
      ],
      orders
        ? revenue /
          orders
        : 0
    );

  return (
    <>

      {/* ================================================== */}
      {/* KPI CARDS */}
      {/* ================================================== */}

      <div
        style={{
          display:
            "grid",
          gridTemplateColumns:
            "repeat(auto-fit,minmax(190px,1fr))",
          gap: 16,
          marginTop: 22,
        }}
      >

        <Card
          title="Revenue"
          value={formatCurrency(
            revenue
          )}
          subtitle="Enterprise sales"
        />

        <Card
          title="Profit"
          value={formatCurrency(
            profit
          )}
          subtitle="Operating profit"
        />

        <Card
          title="Profit Margin"
          value={formatPercent(
            margin
          )}
          subtitle="Revenue efficiency"
        />

        <Card
          title="Orders"
          value={formatNumber(
            orders
          )}
          subtitle="Transaction volume"
        />

        <Card
          title="Quantity"
          value={formatNumber(
            quantity
          )}
          subtitle="Units sold"
        />

        <Card
          title="AOV"
          value={formatCurrency(
            aov
          )}
          subtitle="Average order value"
        />

      </div>


      {/* ================================================== */}
      {/* MONTHLY */}
      {/* ================================================== */}

      <Section
        title="Monthly Performance"
        subtitle="Revenue and operating performance over time"
      >

        <DataTable
          columns={[
            "month",
            "revenue",
            "profit",
            "orders",
          ]}
          rows={
            data.monthly ||
            []
          }
        />

      </Section>


      {/* ================================================== */}
      {/* REGIONAL */}
      {/* ================================================== */}

      <Section
        title="Regional Performance"
        subtitle="Revenue and profitability by operating region"
      >

        <DataTable
          columns={[
            "region",
            "revenue",
            "profit",
            "profit_margin",
            "orders",
          ]}
          rows={
            data.regional ||
            []
          }
        />

      </Section>


      {/* ================================================== */}
      {/* PRODUCTS */}
      {/* ================================================== */}

      <Section
        title="Product Profitability"
        subtitle="Product-level revenue, cost and profit intelligence"
      >

        <DataTable
          columns={[
            "product",
            "revenue",
            "cost",
            "profit",
            "profit_margin",
          ]}
          rows={
            data.profitability ||
            []
          }
        />

      </Section>


      {/* ================================================== */}
      {/* RANKING */}
      {/* ================================================== */}

      <Section
        title="Product Ranking"
        subtitle="Products ranked by revenue and profitability"
      >

        <DataTable
          columns={[
            "rank",
            "product",
            "revenue",
            "profit",
          ]}
          rows={
            data.ranking ||
            []
          }
        />

      </Section>


      {/* ================================================== */}
      {/* CATEGORIES */}
      {/* ================================================== */}

      <Section
        title="Category Performance"
        subtitle="Business performance across product categories"
      >

        <DataTable
          columns={[
            "category",
            "revenue",
            "profit",
            "orders",
          ]}
          rows={
            data.categories ||
            []
          }
        />

      </Section>


      {/* ================================================== */}
      {/* DISCOUNTS */}
      {/* ================================================== */}

      <Section
        title="Discount Intelligence"
        subtitle="Discount levels and associated business performance"
      >

        <DataTable
          columns={[
            "discount",
            "revenue",
            "profit",
            "orders",
          ]}
          rows={
            data.discounts ||
            []
          }
        />

      </Section>

    </>
  );
}


// ============================================================
// COMPARISON DASHBOARD
// ============================================================

function ComparisonDashboard({
  data,
}: {
  data: DashboardData;
}) {

  const files =
    data.files || [];

  const comparison =
    data.comparison || {};

  const metrics =
    comparison
      .metric_comparison ||
    [];

  return (
    <>

      {/* ================================================== */}
      {/* COMPARISON HEADER */}
      {/* ================================================== */}

      <section
        style={{
          marginTop: 22,
          background:
            "linear-gradient(135deg,#0f172a,#1e293b)",
          color:
            "#ffffff",
          borderRadius: 18,
          padding: 26,
        }}
      >

        <div
          style={{
            fontSize: 12,
            fontWeight: 800,
            color:
              "#93c5fd",
            letterSpacing:
              "0.08em",
          }}
        >
          MULTI-FILE COMPARISON
        </div>

        <h2
          style={{
            margin:
              "8px 0 0",
            fontSize: 28,
          }}
        >
          Cross-File Business Intelligence
        </h2>

        <p
          style={{
            color:
              "#cbd5e1",
          }}
        >
          Comparing{" "}
          {files.length}{" "}
          business datasets
          using semantic business
          fields.
        </p>

      </section>


      {/* ================================================== */}
      {/* FILE SUMMARY */}
      {/* ================================================== */}

      <Section
        title="File Comparison"
        subtitle="Individual metrics for every uploaded dataset"
      >

        <DataTable
          columns={[
            "filename",
            "rows",
            "columns",
            "quality",
            "revenue",
            "profit",
            "orders",
            "quantity",
          ]}
          rows={files.map(
            (file: any) => {

              const kpis =
                file
                  ?.business_analysis
                  ?.kpis || {};

              return {
                filename:
                  file.filename,

                rows:
                  file
                    ?.dataset
                    ?.rows ??
                  0,

                columns:
                  file
                    ?.dataset
                    ?.columns ??
                  0,

                quality:
                  file
                    ?.quality
                    ?.score ??
                  0,

                revenue:
                  kpis.total_revenue ??
                  0,

                profit:
                  kpis.total_profit ??
                  0,

                orders:
                  kpis.total_orders ??
                  0,

                quantity:
                  kpis.total_quantity ??
                  0,
              };
            }
          )}
        />

      </Section>


      {/* ================================================== */}
      {/* SEMANTIC MAPPING */}
      {/* ================================================== */}

      <Section
        title="Business Semantic Mapping"
        subtitle="EROI understands equivalent business fields even when column names differ"
      >

        <div
          style={{
            display:
              "grid",
            gridTemplateColumns:
              "repeat(auto-fit,minmax(240px,1fr))",
            gap: 14,
          }}
        >

          <div
            style={infoBoxStyle}
          >
            <strong>
              Common Business Fields
            </strong>

            <div
              style={infoValueStyle}
            >
              {comparison
                .common_business_fields
                ?.join(", ") ||
                "None"}
            </div>
          </div>

          <div
            style={infoBoxStyle}
          >
            <strong>
              Physical Common Columns
            </strong>

            <div
              style={infoValueStyle}
            >
              {comparison
                .common_columns
                ?.join(", ") ||
                "None"}
            </div>
          </div>

          <div
            style={infoBoxStyle}
          >
            <strong>
              All Business Fields
            </strong>

            <div
              style={infoValueStyle}
            >
              {comparison
                .all_business_fields
                ?.join(", ") ||
                "None"}
            </div>
          </div>

        </div>

      </Section>


      {/* ================================================== */}
      {/* METRIC COMPARISON */}
      {/* ================================================== */}

      <Section
        title="Business Metric Comparison"
        subtitle="Relative differences between uploaded datasets"
      >

        {metrics.map(
          (
            metric: any
          ) => (

            <div
              key={
                metric.key
              }
              style={{
                marginBottom:
                  16,
                padding: 18,
                border:
                  "1px solid #e2e8f0",
                borderRadius: 14,
              }}
            >

              <h3
                style={{
                  margin:
                    "0 0 12px",
                  color:
                    "#0f172a",
                }}
              >
                {metric.metric}
              </h3>

              <div
                style={{
                  display:
                    "grid",
                  gridTemplateColumns:
                    "repeat(auto-fit,minmax(220px,1fr))",
                  gap: 12,
                }}
              >

                {metric.values?.map(
                  (
                    item: any,
                    index: number
                  ) => {

                    const currency =
                      metric.key ===
                        "total_revenue" ||
                      metric.key ===
                        "total_profit" ||
                      metric.key ===
                        "aov";

                    const percent =
                      metric.key ===
                      "profit_margin";

                    return (
                      <div
                        key={
                          item.filename
                        }
                        style={{
                          background:
                            "#f8fafc",
                          borderRadius:
                            10,
                          padding:
                            15,
                        }}
                      >

                        <div
                          style={{
                            fontSize:
                              12,
                            color:
                              "#64748b",
                            fontWeight:
                              700,
                          }}
                        >
                          {
                            item.filename
                          }
                        </div>

                        <div
                          style={{
                            marginTop:
                              6,
                            fontSize:
                              22,
                            fontWeight:
                              850,
                            color:
                              "#0f172a",
                          }}
                        >
                          {currency
                            ? formatCurrency(
                                item.value
                              )
                            : percent
                            ? formatPercent(
                                item.value
                              )
                            : formatNumber(
                                item.value
                              )}
                        </div>

                        {index >
                          0 && (
                          <div
                            style={{
                              marginTop:
                                6,
                              fontSize:
                                12,
                              fontWeight:
                                800,
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
                            )}

                            {" ("}

                            {item.change_percent >=
                            0
                              ? "+"
                              : ""}

                            {formatNumber(
                              item.change_percent
                            )}

                            {"%)"}
                          </div>
                        )}

                      </div>
                    );
                  }
                )}

              </div>

            </div>
          )
        )}

      </Section>

    </>
  );
}


const infoBoxStyle: React.CSSProperties =
  {
    background:
      "#f8fafc",
    border:
      "1px solid #e2e8f0",
    borderRadius: 12,
    padding: 16,
    color: "#475569",
  };


const infoValueStyle: React.CSSProperties =
  {
    marginTop: 8,
    color: "#0f172a",
    fontWeight: 700,
    lineHeight: 1.6,
    wordBreak:
      "break-word",
  };


// ============================================================
// MAIN PAGE
// ============================================================

export default function Home() {

  const [
    dashboard,
    setDashboard,
  ] =
    useState<DashboardData | null>(
      null
    );

  const [
    loading,
    setLoading,
  ] =
    useState(true);

  const [
    error,
    setError,
  ] =
    useState("");


  // ==========================================================
  // LOAD WAREHOUSE
  // ==========================================================

  const loadWarehouseDashboard =
    useCallback(
      async () => {

        setLoading(true);
        setError("");

        try {

          const [
            kpiResponse,
            monthlyResponse,
            categoryResponse,
            regionalResponse,
            profitabilityResponse,
            rankingResponse,
            discountResponse,
          ] =
            await Promise.all([
              apiFetch(
                "/analytics/kpis"
              ),

              apiFetch(
                "/analytics/monthly"
              ),

              apiFetch(
                "/analytics/categories"
              ),

              apiFetch(
                "/analytics/regional-performance"
              ),

              apiFetch(
                "/analytics/product-profitability"
              ),

              apiFetch(
                "/analytics/products/ranking?limit=10"
              ),

              apiFetch(
                "/analytics/discounts"
              ),
            ]);


          setDashboard({
            mode:
              "warehouse",

            sourceName:
              "PostgreSQL Enterprise Warehouse",

            kpis:
              kpiResponse,

            monthly:
              extractArray(
                monthlyResponse,
                [
                  "monthly",
                  "data",
                  "results",
                ]
              ),

            regional:
              extractArray(
                regionalResponse,
                [
                  "regional_performance",
                  "regions",
                  "data",
                  "results",
                ]
              ),

            profitability:
              extractArray(
                profitabilityResponse,
                [
                  "product_profitability",
                  "products",
                  "data",
                  "results",
                ]
              ),

            ranking:
              extractArray(
                rankingResponse,
                [
                  "ranking",
                  "products",
                  "data",
                  "results",
                ]
              ),

            categories:
              extractArray(
                categoryResponse,
                [
                  "categories",
                  "data",
                  "results",
                ]
              ),

            discounts:
              extractArray(
                discountResponse,
                [
                  "discounts",
                  "data",
                  "results",
                ]
              ),
          });

        } catch (
          err
        ) {

          setError(
            err instanceof Error
              ? err.message
              : "Unable to load EROI analytics."
          );

        } finally {

          setLoading(
            false
          );
        }

      },
      []
    );


  useEffect(() => {

    loadWarehouseDashboard();

  }, [
    loadWarehouseDashboard,
  ]);


  // ==========================================================
  // FILE ANALYSIS CALLBACK
  // ==========================================================

  function handleUploadedAnalysis(
    result: any
  ) {

    console.log(
      "EROI uploaded result:",
      result
    );

    if (!result) {
      return;
    }

    /*
     * SINGLE FILE
     */

    if (
      result.mode ===
      "single"
    ) {

      setDashboard({
        mode: "single",

        sourceName:
          result.sourceName,

        kpis:
          result.kpis || {},

        monthly:
          result.monthly || [],

        regional:
          result.regional || [],

        profitability:
          result.profitability ||
          [],

        ranking:
          result.ranking || [],

        categories:
          result.categories ||
          [],

        discounts:
          result.discounts ||
          [],

        quality:
          result.quality,

        semantic:
          result.semantic,
      });

      setError("");

      window.scrollTo({
        top: 0,
        behavior: "smooth",
      });

      return;
    }


    /*
     * MULTIPLE FILES
     */

    if (
      result.mode ===
      "comparison"
    ) {

      setDashboard({
        mode:
          "comparison",

        sourceName:
          result.sourceName,

        kpis: {},

        monthly: [],

        regional: [],

        profitability: [],

        ranking: [],

        categories: [],

        discounts: [],

        comparison:
          result.comparison,

        files:
          result.files || [],
      });

      setError("");

      window.scrollTo({
        top: 0,
        behavior: "smooth",
      });

      return;
    }

  }


  // ==========================================================
  // RESET
  // ==========================================================

  function resetToWarehouse() {

    loadWarehouseDashboard();

  }


  // ==========================================================
  // UI
  // ==========================================================

  return (
    <main
      style={{
        minHeight:
          "100vh",

        background:
          "linear-gradient(180deg,#f8fafc 0%,#eef2f7 100%)",

        padding:
          "32px 20px 60px",
      }}
    >

      <div
        style={{
          maxWidth:
            1450,
          margin:
            "0 auto",
        }}
      >

        {/* ================================================= */}
        {/* HEADER */}
        {/* ================================================= */}

        <header
          style={{
            background:
              "linear-gradient(135deg,#0f172a,#1e293b)",

            borderRadius:
              22,

            padding:
              30,

            color:
              "#ffffff",

            boxShadow:
              "0 15px 40px rgba(15,23,42,0.16)",
          }}
        >

          <div
            style={{
              display:
                "flex",

              justifyContent:
                "space-between",

              alignItems:
                "center",

              gap: 20,

              flexWrap:
                "wrap",
            }}
          >

            <div>

              <div
                style={{
                  fontSize: 12,
                  fontWeight: 800,
                  letterSpacing:
                    "0.12em",
                  color:
                    "#93c5fd",
                }}
              >
                ENTERPRISE INTELLIGENCE
              </div>

              <h1
                style={{
                  margin:
                    "8px 0 0",
                  fontSize: 34,
                  fontWeight: 900,
                }}
              >
                EROI
              </h1>

              <p
                style={{
                  margin:
                    "8px 0 0",
                  color:
                    "#cbd5e1",
                  fontSize: 15,
                }}
              >
                Enterprise Revenue &
                Operations Intelligence
                Platform
              </p>

              {dashboard && (
                <div
                  style={{
                    marginTop:
                      12,
                    display:
                      "inline-block",
                    padding:
                      "6px 12px",
                    borderRadius:
                      999,
                    background:
                      "rgba(255,255,255,0.1)",
                    color:
                      "#bfdbfe",
                    fontSize: 12,
                    fontWeight: 700,
                  }}
                >

                  {dashboard.mode ===
                  "warehouse"
                    ? "WAREHOUSE DATA"
                    : dashboard.mode ===
                      "single"
                    ? `FILE ANALYSIS • ${
                        dashboard.sourceName ||
                        "Uploaded File"
                      }`
                    : "MULTI-FILE COMPARISON"}

                </div>
              )}

            </div>


            <button
              type="button"
              onClick={
                resetToWarehouse
              }
              disabled={
                loading
              }
              style={{
                border:
                  "1px solid rgba(255,255,255,0.2)",

                background:
                  "rgba(255,255,255,0.08)",

                color:
                  "#ffffff",

                padding:
                  "11px 18px",

                borderRadius:
                  10,

                cursor:
                  loading
                    ? "not-allowed"
                    : "pointer",

                fontWeight:
                  800,
              }}
            >
              {loading
                ? "Refreshing..."
                : "Reset to Warehouse"}
            </button>

          </div>

        </header>


        {/* ================================================= */}
        {/* ERROR */}
        {/* ================================================= */}

        {error && (
          <div
            style={{
              marginTop:
                20,

              padding:
                16,

              borderRadius:
                14,

              background:
                "#fef2f2",

              border:
                "1px solid #fecaca",

              color:
                "#991b1b",

              fontWeight:
                700,
            }}
          >
            {error}
          </div>
        )}


        {/* ================================================= */}
        {/* DASHBOARD MODE SWITCH */}
        {/* ================================================= */}

        {dashboard?.mode ===
          "comparison" ? (

          <ComparisonDashboard
            data={
              dashboard
            }
          />

        ) : dashboard ? (

          <Dashboard
            data={
              dashboard
            }
          />

        ) : null}


        {/* ================================================= */}
        {/* INITIAL LOADING */}
        {/* ================================================= */}

        {!dashboard &&
          loading && (
            <div
              style={{
                marginTop:
                  30,
                padding:
                  30,
                textAlign:
                  "center",
                background:
                  "#ffffff",
                borderRadius:
                  16,
              }}
            >
              Loading EROI...
            </div>
          )}


        {/* ================================================= */}
        {/* FILE INTELLIGENCE */}
        {/* ================================================= */}

        <MultiFileAnalysis
          onAnalysisComplete={
            handleUploadedAnalysis
          }
        />


        {/* ================================================= */}
        {/* FOOTER */}
        {/* ================================================= */}

        <footer
          style={{
            marginTop:
              35,
            textAlign:
              "center",
            color:
              "#94a3b8",
            fontSize:
              12,
          }}
        >
          EROI 2.0 • Enterprise Revenue &
          Operations Intelligence Platform
        </footer>

      </div>

    </main>
  );
}