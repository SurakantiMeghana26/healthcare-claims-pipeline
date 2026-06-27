{{
    config(
        materialized='table',
        schema='marts'
    )
}}

WITH date_spine AS (
    SELECT DATEADD('day', SEQ4(), '2020-01-01'::DATE) AS date_day
    FROM TABLE(GENERATOR(ROWCOUNT => 2557))
),

final AS (
    SELECT
        TO_NUMBER(TO_CHAR(date_day, 'YYYYMMDD')) AS date_key,
        date_day AS date,
        YEAR(date_day) AS year,
        QUARTER(date_day) AS quarter,
        MONTH(date_day) AS month,
        DAY(date_day) AS day_of_month,
        DAYOFWEEK(date_day) AS day_of_week,
        MONTHNAME(date_day) AS month_name,
        DAYNAME(date_day) AS day_name,
        'Q' || QUARTER(date_day) AS quarter_name,
        
        CASE
            WHEN DAYOFWEEK(date_day) IN (0, 6) THEN TRUE
            ELSE FALSE
        END AS is_weekend,
        
        CURRENT_TIMESTAMP() AS loaded_at
    FROM date_spine
)

SELECT * FROM final
ORDER BY date