{{
    config(
        materialized='view',
        schema='staging'
    )
}}

-- ============================================================
-- Staging Model: stg_providers
-- Source: raw_data.raw_providers
-- Purpose: Clean and standardize provider data
-- ============================================================

WITH source_data AS (

    SELECT * FROM {{ source('raw_data', 'raw_providers') }}

),

cleaned AS (

    SELECT
        -- IDs
        PROVIDER_ID AS provider_id,
        
        -- Provider info
        TRIM(PROVIDER_NAME) AS provider_name,
        PROVIDER_TYPE AS provider_type,
        TRIM(SPECIALTY) AS specialty,
        NPI_NUMBER AS npi_number,
        
        -- Location
        TRIM(ADDRESS) AS address,
        TRIM(CITY) AS city,
        UPPER(TRIM(STATE)) AS state,
        ZIP_CODE AS zip_code,
        PHONE AS phone,
        
        -- Status
        IS_ACTIVE AS is_active,
        
        -- Metadata
        CURRENT_TIMESTAMP() AS loaded_at
        
    FROM source_data

)

SELECT * FROM cleaned