{{
    config(
        materialized='table',
        schema='marts'
    )
}}

-- ============================================================
-- Mart Model: dim_providers
-- Purpose: Provider dimension with claim metrics
-- ============================================================

WITH providers AS (

    SELECT * FROM {{ ref('stg_providers') }}

),

provider_metrics AS (

    SELECT
        provider_id,
        COUNT(*) AS total_claims,
        SUM(billed_amount) AS total_billed,
        SUM(paid_amount) AS total_paid,
        AVG(approval_rate_pct) AS avg_approval_rate,
        SUM(CASE WHEN is_denied THEN 1 ELSE 0 END) AS denied_claims
    FROM {{ ref('stg_claims') }}
    GROUP BY provider_id

),

final AS (

    SELECT
        -- Surrogate key
        ROW_NUMBER() OVER (ORDER BY p.provider_id) AS provider_key,
        
        -- Natural key
        p.provider_id,
        
        -- Provider info
        p.provider_name,
        p.provider_type,
        p.specialty,
        p.npi_number,
        
        -- Location
        p.address,
        p.city,
        p.state,
        p.zip_code,
        p.phone,
        
        -- Status
        p.is_active,
        
        -- Aggregated metrics
        COALESCE(pm.total_claims, 0) AS total_claims,
        COALESCE(ROUND(pm.total_billed, 2), 0) AS total_billed,
        COALESCE(ROUND(pm.total_paid, 2), 0) AS total_paid,
        COALESCE(ROUND(pm.avg_approval_rate, 2), 0) AS avg_approval_rate,
        COALESCE(pm.denied_claims, 0) AS denied_claims,
        
        -- Provider tier
        CASE
            WHEN pm.total_paid >= 100000 THEN 'Top Provider'
            WHEN pm.total_paid >= 50000 THEN 'High Volume'
            WHEN pm.total_paid >= 10000 THEN 'Medium Volume'
            WHEN pm.total_paid > 0 THEN 'Low Volume'
            ELSE 'No Activity'
        END AS provider_tier,
        
        -- Metadata
        CURRENT_TIMESTAMP() AS loaded_at
        
    FROM providers p
    LEFT JOIN provider_metrics pm ON p.provider_id = pm.provider_id

)

SELECT * FROM final