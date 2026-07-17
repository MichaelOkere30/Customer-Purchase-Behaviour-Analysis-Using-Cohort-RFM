SELECT customerid, SUM(totalprice) AS total_spent
FROM sales
GROUP BY customerid
ORDER BY total_spent DESC
LIMIT 10;