{{
    config(
        materialized='view',
        schema='staging'
    )
}}

WITH source_data AS (
    SELECT * FROM {{ source('raw_data', 'raw_claims') }}
),

cleaned AS (
    SELECT
        -- IDs
        CLAIM_ID AS claim_id,
        MEMBER_ID AS member_id,
        PROVIDER_ID AS provider_id,
        PROCEDURE_ID AS procedure_id,
        DIAGNOSIS_ID AS diagnosis_id,
        
        -- Dates
        SERVICE_DATE AS service_date,
        SUBMITTED_DATE AS submitted_date,
        DATEDIFF('DAY', SERVICE_DATE, SUBMITTED_DATE) AS days_to_submit,
        
        -- Status
        CLAIM_STATUS AS claim_status,
        
        -- Financial
        ROUND(BILLED_AMOUNT, 2) AS billed_amount,
        ROUND(ALLOWED_AMOUNT, 2) AS allowed_amount,
        ROUND(PAID_AMOUNT, 2) AS paid_amount,
        ROUND(PATIENT_RESPONSIBILITY, 2) AS patient_responsibility,
        
        -- Calculated metrics
        CASE
            WHEN CLAIM_STATUS = 'Paid' THEN TRUE
            ELSE FALSE
        END AS is_paid,
        
        CASE
            WHEN CLAIM_STATUS = 'Denied' THEN TRUE
            ELSE FALSE
        END AS is_denied,
        
        -- Approval rate
        CASE
            WHEN BILLED_AMOUNT > 0 THEN ROUND((ALLOWED_AMOUNT / BILLED_AMOUNT) * 100, 2)
            ELSE 0
        END AS approval_rate_pct,
        
        CURRENT_TIMESTAMP() AS loaded_at
    FROM source_data
)

SELECT * FROM cleaned