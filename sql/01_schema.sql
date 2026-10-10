-- Пересоздаём объекты, чтобы файл можно было запускать повторно
DROP VIEW IF EXISTS v_kpi;
DROP TABLE IF EXISTS dim_client;
DROP TABLE IF EXISTS fact_credit_snapshot;

-- Справочник клиентов: кто клиент
CREATE TABLE dim_client AS
SELECT client_id, age, dependents, monthly_income FROM raw_credit;
ALTER TABLE dim_client ADD PRIMARY KEY (client_id);

-- Факты: кредитное поведение клиента и итог (дефолт или нет)
CREATE TABLE fact_credit_snapshot AS
SELECT client_id, revolving_util, debt_ratio, open_credit_lines, real_estate_loans,
       past_due_30_59, past_due_60_89, past_due_90, is_default
FROM raw_credit;

-- KPI портфеля: определены в одном месте, все берут отсюда
CREATE VIEW v_kpi AS
SELECT COUNT(*) AS clients,
       ROUND(AVG(is_default)::numeric, 4) AS default_rate,
       ROUND(AVG((past_due_30_59 >= 1)::int)::numeric, 4) AS early_delinquency_share
FROM fact_credit_snapshot;
