SELECT COUNT(*) AS rows, COUNT(DISTINCT client_id) AS unique_ids
FROM fact_credit_snapshot;

SELECT is_default, COUNT(*) AS clients
FROM fact_credit_snapshot GROUP BY is_default ORDER BY is_default;

SELECT COUNT(*) FILTER (WHERE monthly_income IS NULL) AS null_income,
       COUNT(*) FILTER (WHERE dependents IS NULL)     AS null_dependents,
       COUNT(*) FILTER (WHERE age < 18)               AS age_under_18
FROM dim_client;

SELECT COUNT(*) FILTER (WHERE revolving_util > 1.5) AS util_outliers,
       COUNT(*) FILTER (WHERE past_due_30_59 >= 90) AS past_due_codes_96_98
FROM fact_credit_snapshot;
