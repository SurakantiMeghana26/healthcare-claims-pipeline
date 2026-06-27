{{
    config(
        materialized='view',
        schema='staging'
    )
}}

WITH source_data AS (
    SELECT * FROM {{ source('raw_data', 'raw_members') }}
),

cleaned AS (
    SELECT
        MEMBER_ID AS member_id,
        TRIM(FIRST_NAME) AS first_name,
        TRIM(LAST_NAME) AS last_name,
        GENDER AS gender,
        DATE_OF_BIRTH AS date_of_birth,
        DATEDIFF('YEAR', DATE_OF_BIRTH, CURRENT_DATE()) AS age,
        TRIM(ADDRESS) AS address,
        TRIM(CITY) AS city,
        UPPER(TRIM(STATE)) AS state,
        ZIP_CODE AS zip_code,
        PHONE AS phone,
        LOWER(TRIM(EMAIL)) AS email,
        PLAN_TYPE AS plan_type,
        ENROLLMENT_DATE AS enrollment_date,
        IS_ACTIVE AS is_active,
        CURRENT_TIMESTAMP() AS loaded_at
    FROM source_data
)

SELECT * FROM cleaned