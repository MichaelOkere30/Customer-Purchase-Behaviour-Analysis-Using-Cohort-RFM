"""
Customer Purchase Behaviour Analysis Using Cohort & RFM
=========================================================

Goal: Help an online retail store understand customer behaviour by
answering two questions:
    1. How long do customers keep coming back? (Cohort / Retention Analysis)
    2. Who are our most valuable shoppers? (RFM Segmentation)

Sections:
    1. Data Cleaning & Preprocessing
    2. Cohort Analysis & Customer Retention Heatmap
    3. RFM Customer Segmentation Model
"""

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from sqlalchemy import create_engine


# ---------------------------------------------------------------------------
# 1. Data Cleaning & Preprocessing
# ---------------------------------------------------------------------------
# Goal: Transform raw, messy transaction records into a reliable and
# accurate dataset by handling missing values, negative quantities,
# and errors.

def load_and_clean_data(input_path: str = "online_retail1.parquet",
                         output_path: str = "cleaned_retail.csv") -> pd.DataFrame:
    """Load raw transaction data and return a cleaned DataFrame."""

    raw_df = pd.read_parquet(input_path)
    print(raw_df.head())
    raw_df.info()
    print(raw_df.isnull().sum())

    # Drop rows with missing CustomerID -- these sales can't be attributed
    # to a customer, so they're unusable for customer-level analysis.
    raw_df = raw_df.dropna(subset="CustomerID")

    # Remove returns (negative Quantity). These represent refunds/cancellations,
    # not completed purchases, and would distort revenue and frequency metrics.
    print(f"Negative quantity rows: {(raw_df['Quantity'] < 0).sum()}")
    raw_df = raw_df[raw_df["Quantity"] > 0]

    # Remove exact duplicate rows.
    print(f"Duplicate rows: {raw_df.duplicated().sum()}")
    raw_df = raw_df.drop_duplicates()

    # Calculate revenue per line item
    raw_df["TotalPrice"] = raw_df["Quantity"] * raw_df["UnitPrice"]

    # The dataset contained transactions with a UnitPrice of 0. These likely
    # represent promotional or complimentary items. Since these transactions
    # contribute zero revenue, they were excluded from revenue-based analyses
    # such as Customer Lifetime Value (CLV).
    print(f"Zero-price rows: {(raw_df['UnitPrice'] == 0.0).sum()}")
    sales_df = raw_df[raw_df["UnitPrice"] > 0].copy()

    # Cast CustomerID to int (was float64 due to earlier NaNs) so it
    # imports cleanly into a PostgreSQL INTEGER column.
    sales_df["CustomerID"] = sales_df["CustomerID"].astype(int)

    sales_df.to_csv(output_path, index=False)

    print(f"Final row count: {len(sales_df)}")
    print(f"Unique customers: {sales_df['CustomerID'].nunique()}")

    return sales_df


# ---------------------------------------------------------------------------
# 2. Cohort Analysis & Customer Retention Heatmap
# ---------------------------------------------------------------------------
# Goal: Track customer loyalty over time and visually identify exactly
# when shoppers stop returning to the store.

def build_retention_heatmap(engine,
                             sql_path: str = "sql/cohort_analysis.sql",
                             output_image: str = "images/retention_heatmap.png") -> pd.DataFrame:
    """Run the cohort SQL query, pivot into a retention matrix, and plot it."""

    with open(sql_path) as f:
        cohort_query = f.read()

    cohort_df = pd.read_sql_query(cohort_query, engine)
    print(cohort_df.head())

    # Pivot into a cohort_month x cohort_index matrix
    cohort_matrix = cohort_df.pivot(
        index="cohort_month",
        columns="cohort_index",
        values="active_customers",
    )

    # Convert raw counts to retention percentages relative to Month 0 size
    cohort_sizes = cohort_matrix.iloc[:, 0]
    retention_matrix = cohort_matrix.divide(cohort_sizes, axis=0)

    # Clean up axis labels
    retention_matrix.index = pd.to_datetime(retention_matrix.index).strftime("%Y-%m")
    retention_matrix.columns = retention_matrix.columns.astype(int)

    # Plot heatmap
    plt.figure(figsize=(12, 8))
    plt.title("Customer Retention by Cohort")
    sns.heatmap(retention_matrix, annot=True, fmt=".0%", cmap="YlGnBu",
                vmin=0.0, vmax=0.5)
    plt.ylabel("Cohort Month")
    plt.xlabel("Months Since First Purchase")
    plt.tight_layout()
    plt.savefig(output_image, dpi=150)
    plt.show()

    return retention_matrix


# ---------------------------------------------------------------------------
# 3. RFM Customer Segmentation Model
# ---------------------------------------------------------------------------
# Goal: Segment customers based on purchasing behaviour to support
# targeted marketing campaigns and provide a foundation for future
# predictive models.

def assign_persona(row: pd.Series) -> str:
    r, f, m = row["R_Score"], row["F_Score"], row["M_Score"]

    # Bought recently AND buy often
    if r >= 3 and f >= 3:
        return "Champions"
    # Rarely buy, but spend a lot when they do
    elif f <= 2 and m >= 3:
        return "Big Spenders"
    # Used to buy often, but haven't visited in a long time
    elif r <= 2 and f >= 3:
        return "At Risk"
    # Haven't bought in a long time AND rarely bought
    elif r == 1 and f == 1:
        return "Lost Customers"
    # Bought recently, but only a few times
    elif r >= 3 and f <= 2:
        return "New Customers"
    else:
        return "Typical Customers"


def build_rfm_segments(engine,
                        sql_path: str = "sql/rfm_analysis.sql",
                        output_path: str = "rfm_segments.csv") -> pd.DataFrame:
    """Run the RFM SQL query, score customers, and assign personas."""

    with open(sql_path) as f:
        rfm_query = f.read()

    rfm_df = pd.read_sql_query(rfm_query, engine)
    print(rfm_df.head())

    # Score Recency (Lower days = better score = 4)
    r_labels = range(4, 0, -1)
    rfm_df["R_Score"] = pd.qcut(rfm_df["recency"], q=4, labels=r_labels)

    # Score Frequency and Monetary (Higher = better = 4)
    f_labels = range(1, 5)
    m_labels = range(1, 5)

    # rank(method='first') handles ties in order counts
    rfm_df["F_Score"] = pd.qcut(
        rfm_df["frequency"].rank(method="first"), q=4, labels=f_labels
    )
    rfm_df["M_Score"] = pd.qcut(
        rfm_df["monetary_value"], q=4, labels=m_labels
    )

    # Combine into a segment string (e.g. "444") and a total score
    rfm_df["RFM_Segment"] = (
        rfm_df["R_Score"].astype(str)
        + rfm_df["F_Score"].astype(str)
        + rfm_df["M_Score"].astype(str)
    )
    rfm_df["RFM_Score"] = rfm_df[["R_Score", "F_Score", "M_Score"]].sum(axis=1)

    rfm_df["Persona"] = rfm_df.apply(assign_persona, axis=1)

    rfm_df.to_csv(output_path, index=False)

    return rfm_df


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    sales_df = load_and_clean_data()

    cnxn_string = "postgresql+psycopg2://{username}@{host}:{port}/{database}"
    engine = create_engine(cnxn_string.format(
        username="postgres",
        host="localhost",
        port=5432,
        database="online_retail",
    ))

    retention_matrix = build_retention_heatmap(engine)
    rfm_df = build_rfm_segments(engine)

    print("Analysis completed successfully.")
    print(f"Clean transactions: {len(sales_df):,}")
    print(f"Customers analyzed: {rfm_df.shape[0]:,}")


if __name__ == "__main__":
    main()
