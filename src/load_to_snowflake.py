"""
Snowflake Data Loader
=====================
Loads healthcare CSV files into Snowflake RAW_DATA schema.
"""

import os
import pandas as pd
import snowflake.connector
from snowflake.connector.pandas_tools import write_pandas

# ============================================================
# SNOWFLAKE CONNECTION CONFIG
# ============================================================
# IMPORTANT: Update these with YOUR credentials!
SNOWFLAKE_CONFIG = {
    'user': 'SURAKANTIMEGHANA',  # Your username
    'password': 'Chkraja@261234',  # Your password
    'account': 'darenmg-gg85063',  # Your account ID
    'warehouse': 'COMPUTE_WH',
    'database': 'HEALTHCARE_CLAIMS',
    'schema': 'RAW_DATA',
    'role': 'ACCOUNTADMIN'
}

DATA_DIR = '../data'

# ============================================================
# FILES TO LOAD
# ============================================================
FILES_TO_LOAD = [
    ('providers.csv', 'RAW_PROVIDERS'),
    ('members.csv', 'RAW_MEMBERS'),
    ('procedures.csv', 'RAW_PROCEDURES'),
    ('diagnoses.csv', 'RAW_DIAGNOSES'),
    ('claims.csv', 'RAW_CLAIMS'),
]


def get_connection():
    """Create Snowflake connection."""
    print("Connecting to Snowflake...")
    conn = snowflake.connector.connect(**SNOWFLAKE_CONFIG)
    print("  Connected successfully!")
    return conn


def load_csv_to_snowflake(conn, csv_file, table_name):
    """Load a CSV file to Snowflake table."""
    file_path = f'{DATA_DIR}/{csv_file}'
    
    print(f"\nLoading {csv_file} -> {table_name}")
    
    # Read CSV
    df = pd.read_csv(file_path)
    
    # Convert column names to UPPERCASE (Snowflake convention)
    df.columns = df.columns.str.upper()
    
    print(f"  Rows in CSV: {len(df)}")
    
    # Upload to Snowflake
    success, nchunks, nrows, output = write_pandas(
        conn=conn,
        df=df,
        table_name=table_name,
        auto_create_table=True,
        overwrite=True
    )
    
    if success:
        print(f"  Loaded {nrows} rows to {table_name}")
    else:
        print(f"  Failed to load {table_name}")
    
    return success, nrows


def verify_tables(conn):
    """Verify all tables were created."""
    print("\n" + "=" * 60)
    print("VERIFICATION")
    print("=" * 60)
    
    cursor = conn.cursor()
    cursor.execute("SHOW TABLES IN SCHEMA HEALTHCARE_CLAIMS.RAW_DATA")
    tables = cursor.fetchall()
    
    print(f"\nTotal tables in RAW_DATA: {len(tables)}")
    print("\nTables:")
    for table in tables:
        table_name = table[1]
        # Get row count
        cursor.execute(f"SELECT COUNT(*) FROM RAW_DATA.{table_name}")
        count = cursor.fetchone()[0]
        print(f"  {table_name}: {count:,} rows")
    
    cursor.close()


def main():
    """Main execution."""
    print("=" * 60)
    print("SNOWFLAKE DATA LOADER")
    print("=" * 60)
    
    # Connect
    conn = get_connection()
    
    try:
        # Load all files
        total_rows = 0
        for csv_file, table_name in FILES_TO_LOAD:
            success, nrows = load_csv_to_snowflake(conn, csv_file, table_name)
            if success:
                total_rows += nrows
        
        # Verify
        verify_tables(conn)
        
        print("\n" + "=" * 60)
        print("LOAD COMPLETE!")
        print(f"  Total rows loaded: {total_rows:,}")
        print("=" * 60)
        
    finally:
        conn.close()
        print("\nConnection closed.")


if __name__ == '__main__':
    main()