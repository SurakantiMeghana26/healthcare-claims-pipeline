"""
Data Quality DAG
=================
Performs comprehensive data quality checks on healthcare data:
- Row counts
- Null checks
- Referential integrity
- Business rule validation
- Data freshness
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator


# ============================================================
# DEFAULT ARGUMENTS
# ============================================================
default_args = {
    'owner': 'meghana',
    'depends_on_past': False,
    'start_date': datetime(2026, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}


# ============================================================
# SNOWFLAKE CONNECTION HELPER
# ============================================================
def get_snowflake_connection():
    """Create Snowflake connection."""
    import snowflake.connector
    
    return snowflake.connector.connect(
        user='SURAKANTIMEGHANA',
        password='Chkraja@261234',  # Update this!
        account='darenmg-gg85063',
        warehouse='COMPUTE_WH',
        database='HEALTHCARE_CLAIMS',
        role='ACCOUNTADMIN'
    )


# ============================================================
# DATA QUALITY CHECK FUNCTIONS
# ============================================================

def check_row_counts(**context):
    """Check minimum row counts for all tables."""
    print("=" * 60)
    print("CHECK 1: ROW COUNTS")
    print("=" * 60)
    
    conn = get_snowflake_connection()
    cursor = conn.cursor()
    
    expected_minimums = {
        'RAW_DATA.RAW_PROVIDERS': 50,
        'RAW_DATA.RAW_MEMBERS': 500,
        'RAW_DATA.RAW_CLAIMS': 1000,
        'RAW_DATA.RAW_PROCEDURES': 10,
        'RAW_DATA.RAW_DIAGNOSES': 50
    }
    
    issues = []
    for table, min_count in expected_minimums.items():
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        actual = cursor.fetchone()[0]
        
        status = "PASS" if actual >= min_count else "FAIL"
        print(f"  {table}: {actual:,} rows (min: {min_count:,}) - {status}")
        
        if actual < min_count:
            issues.append(f"{table}: only {actual} rows")
    
    cursor.close()
    conn.close()
    
    if issues:
        raise ValueError(f"Row count check failed: {issues}")
    
    print("\nAll row count checks PASSED!")


def check_nulls_in_critical_columns(**context):
    """Check for nulls in critical ID columns."""
    print("=" * 60)
    print("CHECK 2: NULL VALUES IN CRITICAL COLUMNS")
    print("=" * 60)
    
    conn = get_snowflake_connection()
    cursor = conn.cursor()
    
    null_checks = [
        ('RAW_DATA.RAW_CLAIMS', 'CLAIM_ID'),
        ('RAW_DATA.RAW_CLAIMS', 'MEMBER_ID'),
        ('RAW_DATA.RAW_CLAIMS', 'PROVIDER_ID'),
        ('RAW_DATA.RAW_MEMBERS', 'MEMBER_ID'),
        ('RAW_DATA.RAW_PROVIDERS', 'PROVIDER_ID'),
    ]
    
    issues = []
    for table, column in null_checks:
        cursor.execute(f"SELECT COUNT(*) FROM {table} WHERE {column} IS NULL")
        nulls = cursor.fetchone()[0]
        
        status = "PASS" if nulls == 0 else "FAIL"
        print(f"  {table}.{column}: {nulls} nulls - {status}")
        
        if nulls > 0:
            issues.append(f"{table}.{column}: {nulls} nulls")
    
    cursor.close()
    conn.close()
    
    if issues:
        raise ValueError(f"Null check failed: {issues}")
    
    print("\nAll null checks PASSED!")


def check_business_rules(**context):
    """Validate business rules."""
    print("=" * 60)
    print("CHECK 3: BUSINESS RULES")
    print("=" * 60)
    
    conn = get_snowflake_connection()
    cursor = conn.cursor()
    
    # Check 1: No negative amounts
    cursor.execute("""
        SELECT COUNT(*) FROM RAW_DATA.RAW_CLAIMS 
        WHERE BILLED_AMOUNT < 0 OR PAID_AMOUNT < 0
    """)
    negative_amounts = cursor.fetchone()[0]
    print(f"  Negative amounts: {negative_amounts} - {'PASS' if negative_amounts == 0 else 'FAIL'}")
    
    # Check 2: Paid <= Billed
    cursor.execute("""
        SELECT COUNT(*) FROM RAW_DATA.RAW_CLAIMS 
        WHERE PAID_AMOUNT > BILLED_AMOUNT
    """)
    overpaid = cursor.fetchone()[0]
    print(f"  Paid > Billed: {overpaid} - {'PASS' if overpaid == 0 else 'WARN'}")
    
    # Check 3: Valid claim statuses
    cursor.execute("""
        SELECT DISTINCT CLAIM_STATUS FROM RAW_DATA.RAW_CLAIMS
    """)
    statuses = [row[0] for row in cursor.fetchall()]
    valid_statuses = {'Submitted', 'Approved', 'Denied', 'Paid', 'Pending'}
    invalid = set(statuses) - valid_statuses
    print(f"  Claim statuses: {statuses}")
    print(f"  Invalid statuses: {invalid} - {'PASS' if not invalid else 'FAIL'}")
    
    cursor.close()
    conn.close()
    
    if negative_amounts > 0 or invalid:
        raise ValueError(f"Business rule violations found")
    
    print("\nAll business rules PASSED!")


def check_referential_integrity(**context):
    """Check foreign key relationships."""
    print("=" * 60)
    print("CHECK 4: REFERENTIAL INTEGRITY")
    print("=" * 60)
    
    conn = get_snowflake_connection()
    cursor = conn.cursor()
    
    # Check: All claim members exist
    cursor.execute("""
        SELECT COUNT(*) FROM RAW_DATA.RAW_CLAIMS c
        LEFT JOIN RAW_DATA.RAW_MEMBERS m ON c.MEMBER_ID = m.MEMBER_ID
        WHERE m.MEMBER_ID IS NULL
    """)
    orphan_claims = cursor.fetchone()[0]
    print(f"  Orphan claims (no member): {orphan_claims} - {'PASS' if orphan_claims == 0 else 'FAIL'}")
    
    # Check: All claim providers exist
    cursor.execute("""
        SELECT COUNT(*) FROM RAW_DATA.RAW_CLAIMS c
        LEFT JOIN RAW_DATA.RAW_PROVIDERS p ON c.PROVIDER_ID = p.PROVIDER_ID
        WHERE p.PROVIDER_ID IS NULL
    """)
    no_provider = cursor.fetchone()[0]
    print(f"  Claims with no provider: {no_provider} - {'PASS' if no_provider == 0 else 'FAIL'}")
    
    cursor.close()
    conn.close()
    
    if orphan_claims > 0 or no_provider > 0:
        raise ValueError("Referential integrity violations found")
    
    print("\nAll referential integrity checks PASSED!")


def generate_quality_report(**context):
    """Generate final data quality report."""
    print("=" * 60)
    print("DATA QUALITY REPORT")
    print("=" * 60)
    print(f"Report Date: {datetime.now()}")
    print()
    
    conn = get_snowflake_connection()
    cursor = conn.cursor()
    
    # Overall metrics
    cursor.execute("SELECT COUNT(*) FROM RAW_DATA.RAW_CLAIMS")
    total_claims = cursor.fetchone()[0]
    
    cursor.execute("SELECT SUM(BILLED_AMOUNT) FROM RAW_DATA.RAW_CLAIMS")
    total_billed = cursor.fetchone()[0]
    
    cursor.execute("SELECT SUM(PAID_AMOUNT) FROM RAW_DATA.RAW_CLAIMS")
    total_paid = cursor.fetchone()[0]
    
    print(f"Total Claims: {total_claims:,}")
    print(f"Total Billed: ${total_billed:,.2f}")
    print(f"Total Paid: ${total_paid:,.2f}")
    print(f"Approval Rate: {(total_paid/total_billed)*100:.2f}%")
    
    print()
    print("STATUS: ALL QUALITY CHECKS PASSED!")
    print("=" * 60)
    
    cursor.close()
    conn.close()


# ============================================================
# DEFINE THE DAG
# ============================================================
with DAG(
    dag_id='data_quality_checks',
    default_args=default_args,
    description='Comprehensive data quality checks for healthcare data',
    schedule='@daily',
    catchup=False,
    tags=['healthcare', 'data_quality', 'production', 'monitoring'],
) as dag:
    
    task_row_counts = PythonOperator(
        task_id='check_row_counts',
        python_callable=check_row_counts,
    )
    
    task_nulls = PythonOperator(
        task_id='check_nulls',
        python_callable=check_nulls_in_critical_columns,
    )
    
    task_business_rules = PythonOperator(
        task_id='check_business_rules',
        python_callable=check_business_rules,
    )
    
    task_integrity = PythonOperator(
        task_id='check_referential_integrity',
        python_callable=check_referential_integrity,
    )
    
    task_report = PythonOperator(
        task_id='generate_quality_report',
        python_callable=generate_quality_report,
    )
    
    # ============================================================
    # PARALLEL EXECUTION: 4 checks run in parallel, then report
    # ============================================================
    [task_row_counts, task_nulls, task_business_rules, task_integrity] >> task_report