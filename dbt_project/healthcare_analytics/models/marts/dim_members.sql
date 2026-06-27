{{
    config(
        materialized='table',
        schema='marts'
    )
}}

WITH members AS (
    SELECT * FROM {{ ref('stg_members') }}
),

member_metrics AS (
    SELECT
        member_id,
        COUNT(*) AS total_claims,
        SUM(billed_amount) AS total_billed,
        SUM(paid_amount) AS total_paid,
        SUM(patient_responsibility) AS total_patient_paid
    FROM {{ ref('stg_claims') }}
    GROUP BY member_id
),

final AS (
    SELECT
        ROW_NUMBER() OVER (ORDER BY m.member_id) AS member_key,
        m.member_id,
        m.first_name,
        m.last_name,
        m.first_name || ' ' || m.last_name AS full_name,
        m.gender,
        m.date_of_birth,
        m.age,
        
        CASE
            WHEN m.age < 18 THEN 'Child'
            WHEN m.age < 35 THEN 'Young Adult'
            WHEN m.age < 65 THEN 'Adult'
            ELSE 'Senior'
        END AS age_group,
        
        m.city,
        m.state,
        m.zip_code,
        m.plan_type,
        m.enrollment_date,
        m.is_active,
        
        COALESCE(mm.total_claims, 0) AS total_claims,
        COALESCE(ROUND(mm.total_billed, 2), 0) AS total_billed,
        COALESCE(ROUND(mm.total_paid, 2), 0) AS total_paid,
        COALESCE(ROUND(mm.total_patient_paid, 2), 0) AS total_patient_paid,
        
        CASE
            WHEN mm.total_claims >= 10 THEN 'High Utilizer'
            WHEN mm.total_claims >= 5 THEN 'Medium Utilizer'
            WHEN mm.total_claims > 0 THEN 'Low Utilizer'
            ELSE 'No Activity'
        END AS utilization_segment,
        
        CURRENT_TIMESTAMP() AS loaded_at
        
    FROM members m
    LEFT JOIN member_metrics mm ON m.member_id = mm.member_id
)

SELECT * FROM final