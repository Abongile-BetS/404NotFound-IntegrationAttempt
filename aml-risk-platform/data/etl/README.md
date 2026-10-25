# AML/KYC ETL Pipeline

## Overview

The ETL pipeline is responsible for moving source data from CSV files into the AML/KYC application's PostgreSQL data platform.

The pipeline prepares the data in stages so that the same source data can support:

* **Normalized operational data** used by the AML/KYC software
* **Network Intelligence** used to identify relationships between customers, accounts, devices, IPs and other entities
* **Denormalized ML datasets** used for feature engineering, model training and risk scoring

The overall data flow is:

```text
CSV Source
    │
    ▼
CSV Ingestion ETL
    │
    ├── Clean data
    ├── Map source columns
    ├── Validate datatypes
    ├── Reject invalid rows
    └── Batch insert
    │
    ▼
raw.iovation
    │
    ▼
Normalization ETL
    │
    ├── Customer
    ├── Account
    ├── Transactions
    ├── Device
    └── Other entities
    │
    ├───────────────┐
    ▼               ▼
Network          ML Data
Intelligence     Layer
    │               │
    ▼               ▼
Relationships    Features /
& graph signals  training data
```

---

## 1. CSV → Raw Layer

The first stage loads the source CSV into the PostgreSQL `raw` schema.

The current demo source is:

```text
/etl/data/seed/iovation_demo_synthetic_100.csv
```

The ingestion process:

1. Opens the CSV.
2. Reads rows in batches of 10,000.
3. Maps CSV column names to PostgreSQL column names.
4. Cleans empty and placeholder values.
5. Validates values against the `raw.iovation` database schema.
6. Separates valid and rejected rows.
7. Inserts valid rows into `raw.iovation`.
8. Optionally exports rejected rows to a CSV file.

The source-to-target column mapping is defined in `COLUMN_MAPPING`. For example:

```text
Date / Time        → event_timestamp
Tracking Number    → tracking_number
Account            → account_code
Device ID          → device_id
Email Address      → email_address
Mobile Phone Number → mobile_phone_number
Monetary Amount    → monetary_amount
```

The complete mapping is defined in the ingestion script.

### Batch Processing

Rows are processed in batches of 10,000 rather than loading the entire CSV into memory.

```python
for batch in read_batches(reader, 10_000):
    ...
```

This allows the pipeline to process larger datasets without requiring the entire file to be held in memory.

### Validation

Each row is cleaned and validated before insertion.

Invalid rows are rejected when:

* A CSV column is not defined in the mapping.
* A mapped target column does not exist in `raw.iovation`.
* A value does not match the expected PostgreSQL datatype.

### Duplicate Protection

Raw records are inserted using:

```sql
ON CONFLICT (tracking_number) DO NOTHING
```

This prevents an existing tracking number from being inserted again.

---

## 2. Raw → Normalized Layer

Once the raw data has been loaded successfully, the normalization ETL transforms the source data into the application's normalized entities.

The raw layer preserves the source-oriented structure, while the normalized layer creates entities that the AML/KYC application can work with directly.

Example:

```text
raw.iovation
     │
     ├── email_address
     ├── account_code
     ├── device_id
     ├── IP information
     ├── transaction information
     └── behavioural information
              │
              ▼
      Normalization
              │
       ┌──────┼──────┐
       ▼      ▼      ▼
    Customer Account Device
```

For example, customer records are created from customer-related source fields, while accounts are linked back to their corresponding customers.

The normalized data becomes the primary data source for the AML/KYC application's operational functionality.

---

## 3. Normalized Data → Network Intelligence

The normalized entities are also used to construct the Network Intelligence layer.

The purpose of this layer is to represent relationships between entities rather than simply storing individual records.

For example:

```text
Customer
   │
   ├── owns → Account
   │
   ├── uses → Device
   │
   ├── connects from → IP Address
   │
   └── performs → Transaction
```

This allows the system to identify relationships such as:

* Multiple customers using the same device
* Multiple accounts associated with the same device
* Customers sharing IP addresses
* Potential fraud rings
* Connected accounts and behavioural patterns

The Network Intelligence layer can then provide relationship-based signals to the risk engine.

---

## 4. Normalized Data → ML Data Layer

The normalized and network data is also used to create denormalized datasets for machine learning.

The ML layer should contain data structured around the model's requirements rather than the application's normalized entity structure.

For example:

```text
Customer
   +
Transactions
   +
KYC / Screening
   +
Device Signals
   +
Network Signals
   +
Historical Risk
        │
        ▼
   ML Feature Dataset
```

This allows features such as:

* Transaction frequency
* Transaction amounts
* Device sharing
* IP sharing
* Network connections
* Behavioural signals
* Screening results
* Historical alerts

to be combined into model-ready datasets.

The goal is to keep the operational database normalized while providing the ML layer with data that is efficient for feature engineering, training and inference.

---

## 5. Setup

### Requirements

* Docker
* Docker Compose
* PostgreSQL
* Python 3.x
* `psycopg`
* CSV ingestion data file

### Database

The Compose ETL profile reads its database settings from the root
`aml-risk-platform/.env` and connects to the `postgres` service over the
Compose network. No separate ETL `.env` file is needed. On a new PostgreSQL
volume, Compose deploys the schema automatically; existing volumes are not
reset or migrated automatically.

### Backend API

When running the backend outside Docker, set `DATABASE_URL` using the
credentials from `.env` and the published PostgreSQL port. Inside Docker, the
Compose service supplies the container-network URL automatically.

```powershell
$env:DATABASE_URL = "postgresql+psycopg2://<user>:<url-safe-password>@localhost:5480/<database>"
```

The example below shows the URL shape; replace its placeholders with your
database name and URL-safe credentials.

### Source CSV

Place the source CSV in:

```text
/etl/data/seed/
```

The default filename is:

```python
SEED_FILE = "iovation_demo_synthetic_100"
```

The ETL profile mounts `data/db/seed` at `/etl/data/seed` and reads:

```text
/etl/data/seed/iovation_demo_synthetic_100.csv
```

### Run Order

The ETL components should be executed in this order:

```text
1. From `aml-risk-platform`, configure `.env` and start PostgreSQL with `docker compose up -d postgres`.
2. Wait for the database health check; the schema is deployed automatically on first startup with a new volume.
3. Run ingestion and normalized loading with `docker compose --profile etl run --rm etl-engine`.
```

The current Compose ETL job runs raw iovation ingestion and normalized loading
only. Subsequent network, denormalized dataset and analytics steps are not
wired into this container.

---

## 6. Configuration

The ingestion script provides configuration for:

```python
DEBUG_MODE = 1
PRINT_REJECTION_REASONS = False
EXPORT_REJECTION_TO_CSV = False
```

Rejected rows can optionally be exported to:

```text
/etl/data/rejected_iovation_demo_synthetic_100.csv
```

---

## 7. Data Architecture

The ETL is designed around three main data purposes:

### Raw

**Purpose:** Preserve and validate source data.

```text
raw.iovation
```

### Normalized

**Purpose:** Provide clean, relational entities for the AML/KYC application.

```text
public.customer
public.account
...
```

### Analytical / ML

**Purpose:** Combine normalized, transactional and network information into datasets suitable for analytics and machine learning.

```text
ml.*
```

### Network

**Purpose:** Represent relationships between entities and generate network-based risk signals.

```text
network.*
```

The resulting architecture is:

```text
                    CSV
                     │
                     ▼
              ┌─────────────┐
              │     ETL     │
              │ Validation  │
              │   Cleaning  │
              │   Mapping   │
              └──────┬──────┘
                     │
                     ▼
              ┌─────────────┐
              │     RAW     │
              │ raw.iovation│
              └──────┬──────┘
                     │
                     ▼
              ┌─────────────┐
              │ NORMALIZED  │
              │  Customer   │
              │  Account    │
              │ Transactions│
              │   Device    │
              └──────┬──────┘
                     │
              ┌──────┴──────┐
              ▼             ▼
       ┌─────────────┐ ┌─────────────┐
       │   NETWORK   │ │     ML      │
       │ INTELLIGENCE│ │ DENORMALIZED │
       └──────┬──────┘ └──────┬──────┘
              │               │
              └───────┬───────┘
                      ▼
              AML/KYC Risk Engine
```

## Purpose

The ETL layer therefore acts as the **data foundation of the AML/KYC platform**.

It separates source ingestion from application data modelling, while allowing the same source data to feed the application's normalized operational database, Network Intelligence and machine-learning pipelines.
