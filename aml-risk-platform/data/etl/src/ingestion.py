import psycopg
import csv
import os
from datetime import datetime
from pathlib import Path

SEED_FILE = "iovation_demo_synthetic_100"
SEED_FILEPATH = Path(
    os.getenv(
        "SEED_FILEPATH",
        str(
            Path(__file__).resolve().parents[2]
            / "db"
            / "seed"
            / f"{SEED_FILE}.csv"
        ),
    )
)

PRINT_REJECTION_REASONS = True
EXPORT_REJECTION_TO_CSV = False
DEBUG_MODE = 1

COLUMN_MAPPING = {
    "Date / Time": "event_timestamp",
    "Tracking Number": "tracking_number",
    "Result": "result",
    "Integration Point": "integration_point",
    "Rule Set": "rule_set",
    "No. Rules": "rule_count",
    "Matched Rules": "matched_rules",
    "Remote Tool Detected": "remote_tool_detected",
    "Rule": "rule_name",
    "Score": "score",

    # Risk Scores
    "Stated IP Botnet Score": "stated_ip_botnet_score",
    "iovation IP Botnet Score": "iovation_ip_botnet_score",
    "Real IP Botnet Score": "real_ip_botnet_score",
    "Behavioral Analytics Score": "behavioral_analytics_score",
    "SureScore (Global)": "surescore_global",
    "SureScore (Vertical)": "surescore_vertical",

    # Tenant / Account
    "Tenant ID": "tenant_id",
    "Account": "account_code",
    "Device ID": "device_id",

    # Real IP
    "Real IP Address": "real_ip_address",
    "Real IP Proxy Type": "real_ip_proxy_type",
    "Real IP Anonymous Proxy": "real_ip_anonymous_proxy",
    "Real IP ISP": "real_ip_isp",
    "Real IP ISP Org": "real_ip_isp_org",
    "Real IP City": "real_ip_city",
    "Real IP Region": "real_ip_region",
    "Real IP Country": "real_ip_country",

    # Stated IP
    "Stated IP Address": "stated_ip_address",
    "Stated IP ProxyType": "stated_ip_proxy_type",
    "Stated IP Anonymous Proxy": "stated_ip_anonymous_proxy",
    "Stated ISP": "stated_isp",
    "Stated ISP Org": "stated_isp_org",
    "Stated City": "stated_city",
    "Stated Region": "stated_region",
    "Stated Country": "stated_country",

    # iovation IP
    "iovation IP Address": "iovation_ip_address",
    "iovation IP Proxy Type": "iovation_ip_proxy_type",
    "iovation IP Anonymous Proxy": "iovation_ip_anonymous_proxy",
    "iovation ISP": "iovation_isp",
    "iovation ISP Org": "iovation_isp_org",
    "iovation City": "iovation_city",
    "iovation Region": "iovation_region",
    "iovation Country": "iovation_country",

    # Device
    "Blackbox Age": "blackbox_age",
    "Blackbox Date": "blackbox_date",
    "New Device": "new_device",
    "Device Type": "device_type",
    "Recognition Source": "recognition_source",
    "Operating System": "operating_system",
    "Screen Resolution": "screen_resolution",
    "Screen Resolution Irreducible": "screen_resolution_irreducible",
    "Browser Language": "browser_language",
    "Browser Type": "browser_type",
    "Browser Version": "browser_version",
    "Time Zone": "browser_timezone",
    "Flash Enabled": "flash_enabled",
    "Flash Storage Enabled": "flash_storage_enabled",
    "Flash Version": "flash_version",

    # IDs
    "Event ID": "event_id",
    "Service ID": "service_id",
    "Online ID": "online_id",

    # Email
    "Email Address": "email_address",
    "Email Verified": "email_verified",

    # Billing
    "Billing Street": "billing_street",
    "Billing City": "billing_city",
    "Billing Region": "billing_region",
    "Billing Country": "billing_country",
    "Billing Postal Code": "billing_postal_code",

    # Shipping
    "Shipping Street": "shipping_street",
    "Shipping City": "shipping_city",
    "Shipping Region": "shipping_region",
    "Shipping Country": "shipping_country",
    "Shipping Postal Code": "shipping_postal_code",
    "Billing/Shipping Mismatch": "billing_shipping_mismatch",

    # Transaction
    "Monetary Amount": "monetary_amount",
    "Currency Type": "currency_type",
    "Credit Card BIN": "credit_card_bin",
    "ACH Routing Number": "ach_routing_number",

    # Contact
    "Home Phone Number": "home_phone_number",
    "Mobile Phone Number": "mobile_phone_number",
    "Office Phone Number": "office_phone_number",

    # Misc
    "Referrer URL": "referrer_url",
    "Alternate IP": "alternate_ip",
    "SKU": "sku",
    "UPC": "upc",
    "Session Alias": "session_alias",
    "National ID Issuer": "national_id_issuer",
    "Security PIN": "security_pin",
    "Security PIN Type": "security_pin_type",
    "Home Phone Verified": "home_phone_verified",
    "Home Phone SMS Enabled": "home_phone_sms_enabled",
    "Mobile Phone Verified": "mobile_phone_verified",
    "Mobile Phone SMS Enabled": "mobile_phone_sms_enabled",
    "Office Phone Verified": "office_phone_verified",
    "Office Phone SMS Enabled": "office_phone_sms_enabled",

    # Geolocation
    "GPS Spoofing Detected": "gps_spoofing_detected",
    "GPS Spoofing Type": "gps_spoofing_type",
    "Latitude/Longitude": "latitude_longitude",
    "Altitude": "altitude",
    "Geolocation Timestamp": "geolocation_timestamp",
    "Geolocation Accuracy": "geolocation_accuracy",

    # SIM / Network
    "Sim Service": "sim_service",
    "Sim Service Country": "sim_service_country",
    "Carrier Name": "carrier_name",
    "Carrier Country": "carrier_country",

    # Device Hardware
    "Device Hardware ID": "device_hardware_id",
    "Device Manufacturer": "device_manufacturer",
    "Device Brand Name": "device_brand_name",
    "Model ID": "model_id",
    "Device Language": "device_language",
    "Device Currency": "device_currency",
    "Device Orientation": "device_orientation",
    "System Uptime": "system_uptime",
    "Charging Status": "charging_status",
    "Cellular Network Type": "cellular_network_type",
    "Hostname": "hostname",
    "Android SDK Level": "android_sdk_level",
    "Allow Non Market Apps": "allow_non_market_apps",

    # Device Security
    "Jailbreak / Root Detected": "jailbreak_root_detected",
    "Root Evasion Indicated": "root_evasion_indicated",
    "Debug Mode Enabled": "debug_mode_enabled",
    "Executable Name": "executable_name",
    "Application Name": "application_name",
    "Application Version": "application_version",
    "Application Orientation": "application_orientation",
    "Application Signer Id": "application_signer_id",
    "Application Bundle Id": "application_bundle_id",
    "Application Process Name": "application_process_name",

    # Display / Environment
    "Screen Color Depth": "screen_color_depth",
    "Virtual Environment Detected": "virtual_environment_detected",
    "Private Browsing Indicator": "private_browsing_indicator",

    # Transaction / Model Rules
    "TransactionField.rules": "transaction_field_rules",

    # SureScore / Models
    "SureScore (Primary)": "surescore_primary",
    "SureScore (Preview)": "surescore_preview",
    "Advanced Transaction Model (Primary)": "advanced_transaction_model_primary",
    "Advanced Transaction Model (Preview)": "advanced_transaction_model_preview",
    "Behavioral Model (Primary)": "behavioral_model_primary",
    "Behavioral Model (Preview)": "behavioral_model_preview",
    "Behavioral Analytics Score Raw": "behavioral_analytics_score_raw",

    # Fraud / IP Signals
    "Fraud Ring Indicator": "fraud_ring_indicator",
    "IP Signal Score (iovation IP)": "ip_signal_score_iovation_ip",
    "IP Signal Score (Stated IP)": "ip_signal_score_stated_ip",
    "IP Signal Score (Real IP)": "ip_signal_score_real_ip",

    "Last IP Signal Score (iovation IP)": "last_ip_signal_score_iovation_ip",
    "Last IP Signal Score (Stated IP)": "last_ip_signal_score_stated_ip",
    "Last IP Signal Score (Real IP)": "last_ip_signal_score_real_ip",

    "IP Signal Result Codes (iovation IP)": "ip_signal_result_codes_iovation_ip",
    "IP Signal Result Codes (Stated IP)": "ip_signal_result_codes_stated_ip",
    "IP Signal Result Codes (Real IP)": "ip_signal_result_codes_real_ip",

    "IP Signal Score Change Date (iovation IP)": "ip_signal_score_change_date_iovation_ip",
    "IP Signal Score Change Date (Stated IP)": "ip_signal_score_change_date_stated_ip",
    "IP Signal Score Change Date (Real IP)": "ip_signal_score_change_date_real_ip",

    # Transaction Billing
    "TransactionField.tuBillingId": "transaction_field_tu_billing_id",
}

def xprint(msg:str):
    if DEBUG_MODE == 1:
        print(msg)
        

def get_pg_connection():
    conn = psycopg.connect(
        host=os.getenv("PGHOST", "localhost"),
        port=os.getenv("PGPORT", "5480"),
        dbname=os.getenv("PGDATABASE", "aml"),
        user=os.getenv("PGUSER", "aml"),
        password=os.getenv("PGPASSWORD"),
    )
    xprint("Connected to PostgreSQL successfully!")
    return conn


def get_iovation_schema(conn):
        query = """
            SELECT
                column_name,
                data_type
            FROM information_schema.columns
            WHERE table_schema = 'raw'
            AND table_name = 'iovation'
            ORDER BY ordinal_position;
        """
        with conn.cursor() as cursor:
            cursor.execute(query)
            rows = cursor.fetchall()

        return {column_name: data_type for column_name, data_type in rows}

def clean_value(value):

    if value is None:
        return None

    value = value.strip()

    if value == "":
        return None

    if value.upper() in {"N/A", "NA", "NULL"}:
        return None

    return value

def read_batches(reader, batch_size=10_000):

    batch = []

    for row in reader:

        batch.append(row)

        if len(batch) == batch_size:
            yield batch
            batch = []

    if batch:
        yield batch

def validate_value(value, expected_type):

    if value is None:
        return True

    expected_type = expected_type.lower()

    if expected_type in {"character varying", "text"}:
        return isinstance(value, str)

    if expected_type == "integer":
        try:
            int(value)
            return True
        except (ValueError, TypeError):
            return False

    if expected_type == "bigint":
        try:
            int(value)
            return True
        except (ValueError, TypeError):
            return False

    if expected_type == "numeric":
        try:
            float(value)
            return True
        except (ValueError, TypeError):
            return False

    if expected_type == "timestamp with time zone":

        value = value.strip()

        if value.endswith(" SAST"):
            value = value[:-5].strip() + " +0200"

        formats = [
            "%b %d, %Y %I:%M:%S %p %z",
            "%b %d, %Y %I:%M:%S.%f %p %z",
            "%b %d, %Y at %I:%M:%S.%f %p %z",
            "%Y-%m-%d %H:%M:%S%z",
            "%Y-%m-%dT%H:%M:%S%z",
        ]

        for fmt in formats:
            try:
                datetime.strptime(value, fmt)
                return True
            except ValueError:
                continue

        return False

    return True

def validate_row(row, iov_schema):

    errors = []

    cleaned_row = {}

    for csv_column in row:

        if csv_column not in COLUMN_MAPPING:

            errors.append({
                "column": csv_column,
                "reason": "Column is not defined in COLUMN_MAPPING"
            })

            continue

        target_column = COLUMN_MAPPING[csv_column]

        if target_column not in iov_schema:

            errors.append({
                "column": csv_column,
                "reason": f"Target column '{target_column}' does not exist in raw.iovation"
            })

            continue

        value = clean_value(row[csv_column])

        expected_type = iov_schema[target_column]

        if not validate_value(value, expected_type):

            errors.append({
                "column": csv_column,
                "value": value,
                "expected_type": expected_type,
                "reason": "Value does not match expected datatype"
            })

        cleaned_row[target_column] = value

    return cleaned_row, errors

def insert_batch(conn, valid_rows):

    if not valid_rows:
        return

    columns = list(valid_rows[0].keys())

    query = f"""
        INSERT INTO raw.iovation ({", ".join(columns)})
        VALUES ({", ".join(["%s"] * len(columns))})
        ON CONFLICT (tracking_number) DO NOTHING

    """

    values = [
        tuple(row[column] for column in columns)
        for row in valid_rows
    ]

    with conn.cursor() as cursor:
        cursor.executemany(query, values)

    conn.commit()


def save_rejections(rejected_rows, filepath, write_header=False):

    if not rejected_rows:
        return

    fieldnames = list(rejected_rows[0]["row"].keys())

    mode = "w" if write_header else "a"

    with open(
        filepath,
        mode,
        encoding="utf-8",
        newline=""
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames
        )

        if write_header:
            writer.writeheader()


        for rejection in rejected_rows:
            writer.writerow(rejection["row"])


def main():

    print("ETL ingestion pipeline starting...")

    conn = get_pg_connection()

    xprint("Retrieving raw.iovation schema...")
    iov_schema = get_iovation_schema(conn)

    xprint("Starting batch row validation...")

    total_rows = 0
    total_valid = 0
    total_rejected = 0

    with open(
        SEED_FILEPATH,
        "r",
        encoding="utf-8-sig",
        newline=""
    ) as file:

        reader = csv.DictReader(file)

        row_number = 0

        for batch in read_batches(reader, 10_000):

            valid_rows = []
            rejected_rows = []

            for row in batch:

                row_number += 1

                cleaned_row, errors = validate_row(
                    row,
                    iov_schema
                )

                if errors:

                    rejected_rows.append({
                        "row_number": row_number,
                        "row": row,
                        "errors": errors
                    })

                else:

                    valid_rows.append(cleaned_row)

            total_rows += len(batch)
            total_valid += len(valid_rows)
            total_rejected += len(rejected_rows)

            insert_batch(conn, valid_rows)

            if EXPORT_REJECTION_TO_CSV:
                save_rejections(
                    rejected_rows, 
                    REJECT_FILEPATH, 
                    write_header=(total_rows == len(batch))
                )

            print(
                f"Processed batch: {len(batch):,} rows | "
                f"Total processed: {total_rows:,} | "
                f"Valid: {len(valid_rows):,} | "
                f"Rejected: {len(rejected_rows):,}"
            )

    print("\n========== FINAL SUMMARY ==========")
    print(f"Total rows:     {total_rows:,}")
    print(f"Valid rows:     {total_valid:,}")
    print(f"Rejected rows:  {total_rejected:,}")

    if PRINT_REJECTION_REASONS:
        for rejected_row in rejected_rows:

            print(f"\nREJECTED ROW {rejected_row['row_number']}")

            for error in rejected_row["errors"]:

                print(
                    f"  Column: {error.get('column')}"
                    f"\n  Value: {error.get('value')!r}"
                    f"\n  Expected: {error.get('expected_type')}"
                    f"\n  Reason: {error.get('reason')}"
                )

if EXPORT_REJECTION_TO_CSV:
    print(f"===============Exported rejected rows in {REJECT_FILEPATH}")


if __name__ == "__main__":
    main()