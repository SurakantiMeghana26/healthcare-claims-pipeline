"""
Healthcare Data Generator
==========================
Generates synthetic healthcare data for testing the pipeline.
HIPAA-compliant - all data is FAKE!
"""

import os
import random
import pandas as pd
from datetime import datetime, timedelta
from faker import Faker

# Initialize Faker
fake = Faker()
Faker.seed(42)  # For reproducible data
random.seed(42)

# ============================================================
# CONFIGURATION
# ============================================================
NUM_PROVIDERS = 100
NUM_MEMBERS = 1000
NUM_CLAIMS = 5000
NUM_PROCEDURES = 50
NUM_DIAGNOSES = 100

OUTPUT_DIR = '../data'

# ============================================================
# CREATE OUTPUT DIRECTORY
# ============================================================
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)
    print(f"Created directory: {OUTPUT_DIR}")


# ============================================================
# GENERATE PROVIDERS (Doctors/Hospitals)
# ============================================================
def generate_providers():
    """Generate provider (doctor/hospital) data."""
    print("Generating providers...")
    
    specialties = [
        'Cardiology', 'Dermatology', 'Emergency Medicine',
        'Family Medicine', 'Internal Medicine', 'Neurology',
        'Oncology', 'Orthopedics', 'Pediatrics', 'Psychiatry',
        'Radiology', 'Surgery', 'Urology'
    ]
    
    provider_types = ['Hospital', 'Clinic', 'Private Practice', 'Urgent Care']
    
    providers = []
    for i in range(1, NUM_PROVIDERS + 1):
        provider = {
            'provider_id': f'PRV{i:05d}',
            'provider_name': fake.company() + ' Medical',
            'provider_type': random.choice(provider_types),
            'specialty': random.choice(specialties),
            'npi_number': fake.numerify('##########'),  # 10-digit NPI
            'address': fake.street_address(),
            'city': fake.city(),
            'state': fake.state_abbr(),
            'zip_code': fake.zipcode(),
            'phone': fake.phone_number(),
            'is_active': random.choice([True, True, True, False])  # 75% active
        }
        providers.append(provider)
    
    df = pd.DataFrame(providers)
    output_path = f'{OUTPUT_DIR}/providers.csv'
    df.to_csv(output_path, index=False)
    print(f"  Generated {len(df)} providers -> {output_path}")
    return df


# ============================================================
# GENERATE MEMBERS (Patients)
# ============================================================
def generate_members():
    """Generate member (patient) data."""
    print("Generating members...")
    
    plan_types = ['HMO', 'PPO', 'EPO', 'POS', 'HDHP']
    genders = ['M', 'F']
    
    members = []
    for i in range(1, NUM_MEMBERS + 1):
        gender = random.choice(genders)
        birth_date = fake.date_of_birth(minimum_age=18, maximum_age=90)
        enrollment_date = fake.date_between(start_date='-5y', end_date='today')
        
        member = {
            'member_id': f'MBR{i:06d}',
            'first_name': fake.first_name_male() if gender == 'M' else fake.first_name_female(),
            'last_name': fake.last_name(),
            'gender': gender,
            'date_of_birth': birth_date,
            'address': fake.street_address(),
            'city': fake.city(),
            'state': fake.state_abbr(),
            'zip_code': fake.zipcode(),
            'phone': fake.phone_number(),
            'email': fake.email(),
            'plan_type': random.choice(plan_types),
            'enrollment_date': enrollment_date,
            'is_active': random.choice([True, True, True, True, False])  # 80% active
        }
        members.append(member)
    
    df = pd.DataFrame(members)
    output_path = f'{OUTPUT_DIR}/members.csv'
    df.to_csv(output_path, index=False)
    print(f"  Generated {len(df)} members -> {output_path}")
    return df


# ============================================================
# GENERATE PROCEDURES (CPT Codes)
# ============================================================
def generate_procedures():
    """Generate procedure data (CPT codes)."""
    print("Generating procedures...")
    
    procedure_data = [
        ('99213', 'Office visit, established patient', 'E&M', 150.00),
        ('99214', 'Office visit, moderate complexity', 'E&M', 200.00),
        ('80053', 'Comprehensive metabolic panel', 'Lab', 50.00),
        ('85025', 'Complete blood count', 'Lab', 40.00),
        ('71046', 'Chest X-ray, 2 views', 'Radiology', 120.00),
        ('70450', 'CT head without contrast', 'Radiology', 800.00),
        ('45378', 'Colonoscopy, diagnostic', 'Surgery', 1500.00),
        ('27447', 'Total knee arthroplasty', 'Surgery', 25000.00),
        ('93000', 'Electrocardiogram', 'Cardiology', 75.00),
        ('93306', 'Echocardiogram', 'Cardiology', 600.00),
    ]
    
    procedures = []
    for i in range(NUM_PROCEDURES):
        base = procedure_data[i % len(procedure_data)]
        procedure = {
            'procedure_id': f'PROC{i+1:04d}',
            'cpt_code': base[0],
            'procedure_name': base[1],
            'category': base[2],
            'standard_cost': base[3] + random.uniform(-20, 50)
        }
        procedures.append(procedure)
    
    df = pd.DataFrame(procedures)
    output_path = f'{OUTPUT_DIR}/procedures.csv'
    df.to_csv(output_path, index=False)
    print(f"  Generated {len(df)} procedures -> {output_path}")
    return df


# ============================================================
# GENERATE DIAGNOSES (ICD-10 Codes)
# ============================================================
def generate_diagnoses():
    """Generate diagnosis data (ICD-10 codes)."""
    print("Generating diagnoses...")
    
    diagnosis_data = [
        ('I10', 'Essential hypertension', 'Cardiovascular'),
        ('E11.9', 'Type 2 diabetes mellitus', 'Endocrine'),
        ('J45.909', 'Asthma, unspecified', 'Respiratory'),
        ('M79.3', 'Myalgia', 'Musculoskeletal'),
        ('K21.9', 'Gastro-esophageal reflux disease', 'Digestive'),
        ('F32.9', 'Major depressive disorder', 'Mental Health'),
        ('J06.9', 'Acute upper respiratory infection', 'Respiratory'),
        ('N39.0', 'Urinary tract infection', 'Genitourinary'),
        ('M54.5', 'Low back pain', 'Musculoskeletal'),
        ('R51', 'Headache', 'Neurological'),
    ]
    
    diagnoses = []
    for i in range(NUM_DIAGNOSES):
        base = diagnosis_data[i % len(diagnosis_data)]
        diagnosis = {
            'diagnosis_id': f'DX{i+1:04d}',
            'icd10_code': base[0],
            'diagnosis_name': base[1],
            'category': base[2]
        }
        diagnoses.append(diagnosis)
    
    df = pd.DataFrame(diagnoses)
    output_path = f'{OUTPUT_DIR}/diagnoses.csv'
    df.to_csv(output_path, index=False)
    print(f"  Generated {len(df)} diagnoses -> {output_path}")
    return df


# ============================================================
# GENERATE CLAIMS (Insurance Claims)
# ============================================================
def generate_claims(providers_df, members_df, procedures_df, diagnoses_df):
    """Generate insurance claims data."""
    print("Generating claims...")
    
    claim_statuses = ['Submitted', 'Approved', 'Denied', 'Paid', 'Pending']
    status_weights = [0.1, 0.3, 0.1, 0.4, 0.1]  # 40% paid
    
    claims = []
    for i in range(1, NUM_CLAIMS + 1):
        member = members_df.sample(1).iloc[0]
        provider = providers_df.sample(1).iloc[0]
        procedure = procedures_df.sample(1).iloc[0]
        diagnosis = diagnoses_df.sample(1).iloc[0]
        
        service_date = fake.date_between(start_date='-2y', end_date='today')
        submitted_date = service_date + timedelta(days=random.randint(0, 30))
        
        billed_amount = procedure['standard_cost'] * random.uniform(1.5, 3.0)
        allowed_amount = billed_amount * random.uniform(0.4, 0.7)
        paid_amount = allowed_amount * random.uniform(0.8, 1.0)
        
        status = random.choices(claim_statuses, weights=status_weights)[0]
        
        # If denied, paid amount is 0
        if status == 'Denied':
            paid_amount = 0
            allowed_amount = 0
        
        claim = {
            'claim_id': f'CLM{i:07d}',
            'member_id': member['member_id'],
            'provider_id': provider['provider_id'],
            'procedure_id': procedure['procedure_id'],
            'diagnosis_id': diagnosis['diagnosis_id'],
            'service_date': service_date,
            'submitted_date': submitted_date,
            'claim_status': status,
            'billed_amount': round(billed_amount, 2),
            'allowed_amount': round(allowed_amount, 2),
            'paid_amount': round(paid_amount, 2),
            'patient_responsibility': round(allowed_amount - paid_amount, 2)
        }
        claims.append(claim)
    
    df = pd.DataFrame(claims)
    output_path = f'{OUTPUT_DIR}/claims.csv'
    df.to_csv(output_path, index=False)
    print(f"  Generated {len(df)} claims -> {output_path}")
    return df


# ============================================================
# MAIN EXECUTION
# ============================================================
if __name__ == '__main__':
    print("=" * 60)
    print("HEALTHCARE DATA GENERATOR")
    print("=" * 60)
    
    # Generate all data
    providers_df = generate_providers()
    members_df = generate_members()
    procedures_df = generate_procedures()
    diagnoses_df = generate_diagnoses()
    claims_df = generate_claims(providers_df, members_df, procedures_df, diagnoses_df)
    
    print("=" * 60)
    print("Generation Complete!")
    print(f"  Providers: {len(providers_df)}")
    print(f"  Members: {len(members_df)}")
    print(f"  Procedures: {len(procedures_df)}")
    print(f"  Diagnoses: {len(diagnoses_df)}")
    print(f"  Claims: {len(claims_df)}")
    print(f"  Total Records: {len(providers_df) + len(members_df) + len(procedures_df) + len(diagnoses_df) + len(claims_df)}")
    print("=" * 60)