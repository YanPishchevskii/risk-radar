-- 1. Уникальность ключа: строк столько же, сколько уникальных ID
SELECT COUNT(*) AS rows, COUNT(DISTINCT client_id) AS unique_ids
FROM fact_credit_snapshot;

-- 2. Целевая переменная принимает только 0 и 1
SELECT is_default, COUNT(*) AS clients
FROM fact_credit_snapshot GROUP BY is_default ORDER BY is_default;

-- 3. Пропуски и невалидный возраст
SELECT COUNT(*) FILTER (WHERE monthly_income IS NULL) AS null_income,
       COUNT(*) FILTER (WHERE dependents IS NULL)     AS null_dependents,
       COUNT(*) FILTER (WHERE age < 18)               AS age_under_18
FROM dim_client;

-- 4. Аномалии: использование лимитов > 150% и служебные коды просрочек 96/98
SELECT COUNT(*) FILTER (WHERE revolving_util > 1.5) AS util_outliers,
       COUNT(*) FILTER (WHERE past_due_30_59 >= 90) AS past_due_codes_96_98
FROM fact_credit_snapshot;
