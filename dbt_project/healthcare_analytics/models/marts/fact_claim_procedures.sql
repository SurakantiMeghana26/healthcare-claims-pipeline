{{
    config(
        materialized='table',
        schema='marts'
    )
}}

-- ============================================================
-- Fact Model: fact_claim_procedures
-- Grain: ONE ROW PER CLAIM-PROCEDURE COMBINATION
-- Purpose: Procedure-level analytics
-- ============================================================

WITH claims AS (

    SELECT * FROM {{ ref('stg_claims') }}

),

providers_dim AS (
    SELECT * FROM {{ ref('dim_providers') }}
),

members_dim AS (
    SELECT * FROM {{ ref('dim_members') }}
),

procedures_dim AS (
    SELECT * FROM {{ ref('dim_procedures') }}
),

dates_dim AS (
    SELECT * FROM {{ ref('dim_dates') }}
),

claims_fact AS (
    SELECT * FROM {{ ref('fact_claims') }}
),

final AS (
    SELECT
        -- Surrogate key
        ROW_NUMBER() OVER (ORDER BY c.claim_id, c.procedure_id) AS claim_procedure_key,
        
        -- Foreign keys
        cf.claim_key,
        m.member_key,
        p.provider_key,
        proc.procedure_key,
        d.date_key AS service_date_key,
        
        -- Original IDs
        c.claim_id,
        c.procedure_id,
        
        -- Procedure info
        proc.cpt_code,
        proc.procedure_name,
        proc.category AS procedure_category,
        
        -- Financial details
        proc.standard_cost,
        c.billed_amount,
        c.paid_amount,
        
        -- Variance from standard cost
        ROUND(c.billed_amount - proc.standard_cost, 2) AS cost_variance,
        
        CASE
            WHEN c.billed_amount > proc.standard_cost * 1.5 THEN 'Above Standard'
            WHEN c.billed_amount < proc.standard_cost * 0.8 THEN 'Below Standard'
            ELSE 'Within Range'
        END AS cost_variance_category,
        
        -- Status
        c.claim_status,
        c.is_paid,
        
        -- Metadata
        CURRENT_TIMESTAMP() AS loaded_at
        
    FROM claims c
    LEFT JOIN claims_fact cf ON c.claim_id = cf.claim_id
    LEFT JOIN members_dim m ON c.member_id = m.member_id
    LEFT JOIN providers_dim p ON c.provider_id = p.provider_id
    LEFT JOIN procedures_dim proc ON c.procedure_id = proc.procedure_id
    LEFT JOIN dates_dim d ON c.service_date = d.date
)

SELECT * FROM final