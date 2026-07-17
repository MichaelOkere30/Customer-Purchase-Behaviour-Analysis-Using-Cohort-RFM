WITH max_date AS (
    -- Find the most recent date in the entire dataset to act as our "today"
    SELECT MAX(invoicedate) + INTERVAL '1 day' AS ref_date 
    FROM sales
),

rfm_base AS (
    -- Calculate Frequency and Monetary value, and find the last purchase date
    SELECT 
        customerid,
        MAX(invoicedate) AS last_purchase_date,
        COUNT(DISTINCT invoiceno) AS frequency, 
        SUM(totalprice) AS monetary_value
    FROM sales
    GROUP BY customerid
)

-- Put it all together to calculate the Recency in days
SELECT 
    b.customerid,
    -- Calculate days between the reference date and the customer's last purchase
    EXTRACT(DAY FROM (m.ref_date - b.last_purchase_date)) AS recency,
    b.frequency,
    b.monetary_value
FROM rfm_base b
CROSS JOIN max_date m;