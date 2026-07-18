# Customer Purchase Behaviour Analysis Using Cohort & RFM

Understanding how a customer base behaves over time — who keeps coming back,
who's about to churn, and who's worth the most — using cohort retention
analysis and RFM (Recency, Frequency, Monetary) segmentation on real
e-commerce transaction data.

## The Goal

This project helps an online retail store better understand its customers.
By analyzing past sales data, it answers two core questions:

1. **How long do customers keep coming back?**
2. **Who are our most valuable shoppers?**

The output supports targeting the right customers with the right
promotions — whether that's a re-engagement email for lapsing shoppers or a
VIP offer for top spenders.

## Dataset

[UCI Online Retail Dataset](https://archive.ics.uci.edu/dataset/352/online+retail) —
transactional data from a UK-based online retailer, covering invoices,
products, quantities, prices, customer IDs, and countries.

## Tech Stack

- **Python** (pandas, seaborn, matplotlib) — data cleaning and visualization
- **PostgreSQL** — cohort and RFM calculations via SQL
- **SQLAlchemy** — Python-to-database connection

## Repo Structure

```
.
├── customer_purchase_behaviour_analysis.ipynb      # notebook walkthrough
├── online_retail1.parquet                          # raw source data
├── cleaned_retail.csv                               # cleaned transaction data (output)
├── rfm_segments.csv                                 # RFM scores & personas (output)
├── python/
│   └── customer_purchase_behaviour_analysis.py     # cleaning, cohort, RFM pipeline
├── sql/
│   ├── schema.sql                                   # CREATE TABLE statements for online_retail
│   ├── cohort_analysis.sql                         # cohort retention query
│   ├── rfm_analysis.sql                            # recency/frequency/monetary query
│   ├── top_ten_customers.sql                       # top 10 customers by spend
│   ├── total_no_of_customers.sql                   # total unique customer count
│   └── total_sales.sql                             # total revenue query
├── images/
│   └── retention_heatmap.png                       # generated retention heatmap
└── README.md
```

## Analysis Overview

### 1. Data Cleaning & Preprocessing

Raw transaction records were cleaned to produce a reliable dataset:

- Dropped rows with missing `CustomerID` (can't be attributed to a customer)
- Removed returns (negative `Quantity`), which represent refunds/cancellations
  rather than completed purchases
- Removed exact duplicate rows
- Excluded zero-price transactions (promotional/complimentary items) from
  revenue-based analysis
- Cast `CustomerID` to integer for clean import into PostgreSQL

**Result:** 392,692 clean transactions across 4,338 unique customers.

### 2. Cohort Analysis & Customer Retention Heatmap

Customers were grouped into monthly cohorts based on their first purchase
date, then tracked to see what percentage of each cohort returned in each
subsequent month.

**Key findings:**

- Retention drops off sharply after the first month for every cohort —
  most fall from 100% to the 15–25% range by month 1, meaning the majority
  of customers are one-time or occasional buyers.
- The **December 2010 cohort** stands out, retaining noticeably better than
  later cohorts (35–40% through most of the year, spiking to 50% at month
  11) — likely a seasonal effect of holiday shoppers returning the
  following year.
- Later 2011 cohorts have less data (fewer customers, less time observed),
  so their retention numbers are noisier and less reliable than December's.

**Takeaway:** The biggest drop-off happens right after a customer's first
purchase. The highest-leverage intervention is a first-month touchpoint —
a follow-up email, a discount on the next order, or a reminder — to get
customers to a second purchase before they drift away.

### 3. RFM Customer Segmentation Model

Customers were scored on three dimensions using SQL, then segmented with
Python:

- **Recency** — days since last purchase (lower = better)
- **Frequency** — number of purchases (higher = better)
- **Monetary** — total spend (higher = better)

Each customer received a 1–4 score per dimension (via quartile binning),
combined into an `RFM_Segment` string and total `RFM_Score`, then mapped to
a persona:

| Persona | Definition |
|---|---|
| Champions | Bought recently and buy often |
| Big Spenders | Rarely buy, but spend a lot when they do |
| At Risk | Used to buy often, haven't returned in a while |
| Lost Customers | Haven't bought in a long time and rarely bought |
| New Customers | Bought recently, but only a few times |
| Typical Customers | Everyone else |

## How to Run

1. Load `online_retail1.parquet` into a PostgreSQL database (or point the
   script at your own source).
2. Update the `create_engine` connection details in
   `python/customer_purchase_behaviour_analysis.py` for your environment.
3. Run the script:

   ```bash
   python python/customer_purchase_behaviour_analysis.py
   ```

Outputs: `cleaned_retail.csv`, `images/retention_heatmap.png`, and
`rfm_segments.csv`.

## Next Steps

- Extend RFM segmentation into a predictive churn model
- Layer in Customer Lifetime Value (CLV) estimates per segment
- Automate the pipeline as a scheduled job for ongoing monitoring
