# Healthcare Claims ETL Pipeline

> **Production-grade ETL pipeline orchestrated by Apache Airflow with dbt transformations and Snowflake data warehouse**

A complete end-to-end data engineering project demonstrating modern data stack patterns for healthcare claims analytics. This project simulates real-world production workflows used by companies like Cardinal Health, Anthem, and Cleveland Clinic.

---

## Project Overview

This project implements an **automated daily data pipeline** that:

1. Generates synthetic healthcare data (HIPAA-safe)
2. Loads raw data to Snowflake
3. Transforms data through medallion architecture (Raw to Staging to Marts)
4. Validates data quality with 4 parallel checks
5. All orchestrated by Apache Airflow!

### Key Achievements

- Built **4 production Airflow DAGs** with task dependencies
- Custom **Docker image** with dbt and Snowflake integration
- **12 dbt models** implementing Kimball star schema
- Processed **6,250+ healthcare records** (HIPAA-safe synthetic data)
- **Parallel data quality checks** (advanced Airflow pattern)
- **Provider tiering** and **member segmentation** business logic
- Production-grade error handling and monitoring

---

## Architecture

### Data Flow

```
HEALTHCARE APIs (simulated)
       to
APACHE AIRFLOW (orchestrator)
       to
PYTHON SCRIPTS (data generation)
       to
SNOWFLAKE RAW (bronze layer)
       to
dbt STAGING (silver layer)
       to
dbt MARTS (gold layer - star schema)
       to
DATA QUALITY CHECKS (4 parallel checks)
       to
PRODUCTION-READY DATA WAREHOUSE
```

### 3-Layer Medallion Architecture

**Layer 1: RAW (Bronze)**
- 5 source tables loaded from Python data generator
- Schema: `RAW_DATA`
- Volume: ~6,250 records

**Layer 2: STAGING (Silver)**
- 5 cleaned views with business logic
- Calculated fields (age, approval rates)
- Standardized formats

**Layer 3: MARTS (Gold)**
- 5 dimension tables
- 2 fact tables (different grains)
- Kimball star schema
- Ready for BI tools

---

## Star Schema Design

### Dimensions

| Dimension | Description | Rows |
|-----------|-------------|------|
| **dim_providers** | Healthcare providers with revenue tiers | 100 |
| **dim_members** | Patients with utilization segments | 1,000 |
| **dim_procedures** | Medical procedures with CPT codes | 50 |
| **dim_diagnoses** | Diagnoses with ICD-10 codes | 100 |
| **dim_dates** | Time dimension (2020-2026) | 2,557 |

### Facts

| Fact | Grain | Description | Rows |
|------|-------|-------------|------|
| **fact_claims** | One row per claim | Order-level metrics | 5,000 |
| **fact_claim_procedures** | One row per claim+procedure | Procedure analytics | 5,000 |

---

## Airflow DAGs

### 1. hello_healthcare
- First test DAG with 4 sequential tasks
- Demonstrates basic DAG patterns

### 2. healthcare_data_ingestion
- Generates synthetic healthcare data
- Verifies file creation
- Loads data to Snowflake
- 6 tasks in sequence

### 3. dbt_transformation
- Triggers dbt debug, run, and test
- Builds all 12 dbt models
- Validates data with built-in tests
- 5 tasks in sequence

### 4. data_quality_checks
- **4 parallel data quality checks**:
  - Row count validation
  - Null value checks
  - Business rule validation
  - Referential integrity
- Generates final quality report

---

## Tech Stack

| Component | Technology |
|-----------|-----------|
| **Orchestrator** | Apache Airflow 3.0.4 |
| **Data Warehouse** | Snowflake |
| **Transformation** | dbt 1.8.0 |
| **Data Generation** | Python + Faker |
| **Containerization** | Docker + docker-compose |
| **Custom Image** | Built from Airflow base |
| **Version Control** | Git + GitHub |
| **Language** | Python + SQL + Jinja |

---

## Project Structure

```
healthcare-claims-pipeline/
├── airflow/
│   ├── dags/                          # 4 production DAGs
│   │   ├── hello_healthcare_dag.py
│   │   ├── data_ingestion_dag.py
│   │   ├── dbt_transformation_dag.py
│   │   └── data_quality_dag.py
│   ├── config/
│   │   └── profiles.yml               # dbt profile for container
│   ├── Dockerfile                     # Custom Airflow image
│   ├── docker-compose.yaml            # Multi-service config
│   └── requirements.txt
│
├── dbt_project/
│   └── healthcare_analytics/
│       ├── models/
│       │   ├── staging/               # 5 staging models
│       │   │   ├── sources.yml
│       │   │   ├── stg_providers.sql
│       │   │   ├── stg_members.sql
│       │   │   ├── stg_procedures.sql
│       │   │   ├── stg_diagnoses.sql
│       │   │   └── stg_claims.sql
│       │   │
│       │   └── marts/                 # 7 mart models
│       │       ├── dim_providers.sql
│       │       ├── dim_members.sql
│       │       ├── dim_procedures.sql
│       │       ├── dim_diagnoses.sql
│       │       ├── dim_dates.sql
│       │       ├── fact_claims.sql
│       │       └── fact_claim_procedures.sql
│       │
│       └── dbt_project.yml
│
├── src/                               # Python scripts
│   ├── generate_healthcare_data.py    # Synthetic data generator
│   └── load_to_snowflake.py           # Snowflake loader
│
├── data/                              # Generated CSV files
└── README.md
```

---

## Key Features

### 1. Custom Docker Image

Built a custom Airflow image with pre-installed dbt to avoid runtime installation issues:

```dockerfile
FROM apache/airflow:3.0.4
USER airflow
RUN pip install --no-cache-dir \
    dbt-snowflake==1.8.0 \
    faker==25.0.0 \
    pandas==2.2.2 \
    snowflake-connector-python==3.10.0
```

### 2. Parallel Task Execution

The data quality DAG demonstrates parallel processing:

```python
[task_row_counts, task_nulls, task_business_rules, task_integrity] >> task_report
```

4 checks run simultaneously, then report is generated.

### 3. Business Logic in Transformations

- **Provider Tiering**: Top Provider, High Volume, Medium Volume, Low Volume
- **Member Utilization**: High Utilizer, Medium, Low, No Activity
- **Age Groups**: Child, Young Adult, Adult, Senior
- **Cost Tiers**: High Cost, Medium Cost, Standard Cost, Low Cost
- **Submission Speed**: Fast, Normal, Slow, Very Slow

---

## Business Insights Enabled

This data warehouse enables analytics like:

- Provider performance and revenue analysis
- Member utilization and segmentation
- Procedure cost analysis
- Claim approval rate trends
- Geographic distribution of care
- Delivery and submission performance
- Denied claims analysis

---

## Sample Queries

### Top Providers by Revenue

```sql
SELECT 
    provider_name,
    specialty,
    provider_tier,
    total_claims,
    total_paid
FROM dim_providers
WHERE provider_tier = 'Top Provider'
ORDER BY total_paid DESC
LIMIT 10;
```

### Member Utilization Analysis

```sql
SELECT 
    age_group,
    utilization_segment,
    COUNT(*) AS member_count,
    AVG(total_paid) AS avg_paid
FROM dim_members
GROUP BY age_group, utilization_segment
ORDER BY age_group;
```

### Claim Status Distribution

```sql
SELECT 
    claim_status,
    COUNT(*) AS claims,
    SUM(billed_amount) AS billed,
    SUM(paid_amount) AS paid,
    AVG(approval_rate_pct) AS avg_approval
FROM fact_claims
GROUP BY claim_status;
```

---

## Production Patterns Demonstrated

- Multi-service Docker architecture
- Custom Docker images for dependencies
- Airflow DAG dependencies and parallelism
- Volume mounting for shared code
- Environment-based configuration
- Connection management
- Data quality monitoring
- Idempotent transformations
- Error handling and retries
- Comprehensive logging

---

## Lessons Learned

This project taught me real-world data engineering challenges:

1. **Library dependencies in containers** - Solved with custom Docker image
2. **JWT secret configuration** - Required for Airflow 3.x APIs
3. **Schema naming conflicts** - Resolved with macro adjustments
4. **Worker executor choices** - LocalExecutor vs CeleryExecutor
5. **File encoding issues** - Windows Notepad vs Linux containers
6. **dbt internal macro errors** - Fixed with stable version pinning

---

## Future Enhancements

- Add Slack notifications for failures
- Implement SLA monitoring
- Build incremental dbt models for large facts
- Add dbt exposures for BI dashboards
- Set up CI/CD with GitHub Actions
- Add data lineage documentation
- Connect to Power BI/Tableau for visualization

---

## Author

**Surakanti Meghana**
- Location: Dublin, Ohio
- GitHub: [@SurakantiMeghana26](https://github.com/SurakantiMeghana26)

---

## License

MIT License

---

**If you found this project helpful, please star the repository!**
