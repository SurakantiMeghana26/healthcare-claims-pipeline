{{
    config(
        materialized='view',
        schema='staging'
    )
}}

WITH source_data AS (
    SELECT * FROM {{ source('raw_data', 'raw_procedures') }}
),

cleaned AS (
    SELECT
        PROCEDURE_ID AS procedure_id,
        CPT_CODE AS cpt_code,
        TRIM(PROCEDURE_NAME) AS procedure_name,
        CATEGORY AS category,
        ROUND(STANDARD_COST, 2) AS standard_cost,
        CURRENT_TIMESTAMP() AS loaded_at
    FROM source_data
)

SELECT * FROM cleaned