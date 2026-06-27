{{
    config(
        materialized='table',
        schema='marts'
    )
}}

WITH diagnoses AS (
    SELECT * FROM {{ ref('stg_diagnoses') }}
),

diagnosis_metrics AS (
    SELECT
        diagnosis_id,
        COUNT(*) AS times_diagnosed,
        SUM(paid_amount) AS total_treatment_cost
    FROM {{ ref('stg_claims') }}
    GROUP BY diagnosis_id
),

final AS (
    SELECT
        ROW_NUMBER() OVER (ORDER BY d.diagnosis_id) AS diagnosis_key,
        d.diagnosis_id,
        d.icd10_code,
        d.diagnosis_name,
        d.category,
        
        COALESCE(dm.times_diagnosed, 0) AS times_diagnosed,
        COALESCE(ROUND(dm.total_treatment_cost, 2), 0) AS total_treatment_cost,
        
        CURRENT_TIMESTAMP() AS loaded_at
        
    FROM diagnoses d
    LEFT JOIN diagnosis_metrics dm ON d.diagnosis_id = dm.diagnosis_id
)

SELECT * FROM final