{{
    config(
        materialized='table',
        schema='marts'
    )
}}

-- ============================================================
-- Fact Model: fact_claims
-- Grain: ONE ROW PER CLAIM
-- Purpose: Claim-level facts with foreign keys to all dimensions
-- ============================================================

WITH claims AS (

    SELECT * FROM {{ ref('stg_claims') }}

),

members_dim AS (

    SELECT * FROM {{ ref('dim_members') }}

),

providers_dim AS (

    SELECT * FROM {{ ref('dim_providers') }}

),

procedures_dim AS (

    SELECT * FROM {{ ref('dim_procedures') }}

),

diagnoses_dim AS (

    SELECT * FROM {{ ref('dim_diagnoses') }}

),

dates_dim AS (

    SELECT * FROM {{ ref('dim_dates') }}

),

final AS (

    SELECT
        -- Surrogate key for fact
        ROW_NUMBER() OVER (ORDER BY c.claim_id) AS claim_key,
        
        -- Natural key
        c.claim_id,
        
        -- Foreign keys to dimensions
        m.member_key,
        p.provider_key,
        proc.procedure_key,
        d.diagnosis_key,
        dt.date_key AS service_date_key,
        
        -- Original IDs (for reference)
        c.member_id,
        c.provider_id,
        c.procedure_id,
        c.diagnosis_id,
        
        -- Dates
        c.service_date,
        c.submitted_date,
        c.days_to_submit,
        
        -- Status
        c.claim_status,
        c.is_paid,
        c.is_denied,
        
        -- Financial metrics
        c.billed_amount,
        c.allowed_amount,
        c.paid_amount,
        c.patient_responsibility,
        c.approval_rate_pct,
        
        -- Calculated metrics
        ROUND(c.billed_amount - c.paid_amount, 2) AS write_off_amount,
        
        CASE
            WHEN c.billed_amount >= 10000 THEN 'High Cost'
            WHEN c.billed_amount >= 1000 THEN 'Medium Cost'
            WHEN c.billed_amount >= 100 THEN 'Standard Cost'
            ELSE 'Low Cost'
        END AS claim_size,
        
        -- Submission performance
        CASE
            WHEN c.days_to_submit <= 7 THEN 'Fast'
            WHEN c.days_to_submit <= 14 THEN 'Normal'
            WHEN c.days_to_submit <= 30 THEN 'Slow'
            ELSE 'Very Slow'
        END AS submission_speed,
        
        -- Metadata
        CURRENT_TIMESTAMP() AS loaded_at
        
    FROM claims c
    LEFT JOIN members_dim m ON c.member_id = m.member_id
    LEFT JOIN providers_dim p ON c.provider_id = p.provider_id
    LEFT JOIN procedures_dim proc ON c.procedure_id = proc.procedure_id
    LEFT JOIN diagnoses_dim d ON c.diagnosis_id = d.diagnosis_id
    LEFT JOIN dates_dim dt ON c.service_date = dt.date

)

SELECT * FROM final