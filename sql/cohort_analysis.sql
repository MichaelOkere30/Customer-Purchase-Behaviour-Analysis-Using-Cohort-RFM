-- Step 1: Find each customer's first purchase month
WITH first_purchase AS (
    SELECT 
        customerid,
		-- Get the customer's first purchase and keep only the month
        DATE_TRUNC('month', MIN(invoicedate)) AS cohort_month
    FROM sales
    GROUP BY customerid
), 

-- Step 2: Get every month each customer made a purchase
transaction_activity AS (
    SELECT 
        s.customerid,
		-- Customer's first purchase month
        f.cohort_month,
		-- Month of the current transaction
        DATE_TRUNC('month', s.invoicedate) AS activity_month
    FROM sales s
    JOIN first_purchase f ON s.customerid = f.customerid
), 

-- Step 3: Calculate how many months have passed
cohort_index_calc AS (
    SELECT 
        customerid,
        cohort_month,
        -- Number of months between first purchase and current purchase
        ((EXTRACT(year FROM activity_month) - EXTRACT(year FROM cohort_month)) * 12) 
        + (EXTRACT(month FROM activity_month) - EXTRACT(month FROM cohort_month)) AS cohort_index
    FROM transaction_activity
)

-- Step 4: Count active customers in each cohort each month
SELECT 
    cohort_month,
    cohort_index,
    COUNT(DISTINCT customerid) AS active_customers
FROM cohort_index_calc
GROUP BY cohort_month, cohort_index
ORDER BY cohort_month, cohort_index;