{{
    config(
        materialized='table',
        schema='marts'
    )
}}

WITH procedures AS (
    SELECT * FROM {{ ref('stg_procedures') }}
),

procedure_metrics AS (
    SELECT
        procedure_id,
        COUNT(*) AS times_performed,
        AVG(billed_amount) AS avg_billed_amount,
        AVG(paid_amount) AS avg_paid_amount
    FROM {{ ref('stg_claims') }}
    GROUP BY procedure_id
),

final AS (
    SELECT
        ROW_NUMBER() OVER (ORDER BY p.procedure_id) AS procedure_key,
        p.procedure_id,
        p.cpt_code,
        p.procedure_name,
        p.category,
        p.standard_cost,
        
        COALESCE(pm.times_performed, 0) AS times_performed,
        COALESCE(ROUND(pm.avg_billed_amount, 2), 0) AS avg_billed_amount,
        COALESCE(ROUND(pm.avg_paid_amount, 2), 0) AS avg_paid_amount,
        
        CASE
            WHEN p.standard_cost >= 10000 THEN 'High Cost'
            WHEN p.standard_cost >= 1000 THEN 'Medium Cost'
            WHEN p.standard_cost >= 100 THEN 'Standard Cost'
            ELSE 'Low Cost'
        END AS cost_tier,
        
        CURRENT_TIMESTAMP() AS loaded_at
        
    FROM procedures p
    LEFT JOIN procedure_metrics pm ON p.procedure_id = pm.procedure_id
)

SELECT * FROM final