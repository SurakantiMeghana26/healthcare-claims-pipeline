{{
    config(
        materialized='view',
        schema='staging'
    )
}}

WITH source_data AS (
    SELECT * FROM {{ source('raw_data', 'raw_diagnoses') }}
),

cleaned AS (
    SELECT
        DIAGNOSIS_ID AS diagnosis_id,
        ICD10_CODE AS icd10_code,
        TRIM(DIAGNOSIS_NAME) AS diagnosis_name,
        CATEGORY AS category,
        CURRENT_TIMESTAMP() AS loaded_at
    FROM source_data
)

SELECT * FROM cleaned