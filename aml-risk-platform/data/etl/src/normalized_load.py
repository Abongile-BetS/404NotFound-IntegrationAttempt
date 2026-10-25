import uuid
import psycopg
from psycopg import sql
import hashlib 
import random 
from faker import Faker


PG_HOST = "localhost"
PG_PORT = 5480
PG_DATABASE = "aml"
PG_USER = "aml"
PG_PASSWORD = "aml_password"

DEBUG_MODE = 0

# HELPER METHODS
def xprint(msg:str):
    if DEBUG_MODE == 1:
        print(msg)

def get_pg_connection():
    try:
        conn = psycopg.connect(
            host=PG_HOST,
            port=PG_PORT,
            dbname=PG_DATABASE,
            user=PG_USER,
            password=PG_PASSWORD,
        )

        print("Connected to PostgreSQL successfully!")
        return conn

    except Exception as e:
        print(f"PostgreSQL connection failed: {e}")
        return None


def execute_query(conn, query, params=None, fetch=False):
    """
    Execute a SQL query.

    Parameters
    ----------
    conn : psycopg connection
        Active database connection.

    query : str
        SQL query to execute.

    params : tuple/list/dict, optional
        Parameters for the SQL query.

    fetch : bool
        If True, return all rows returned by the query.

    Returns
    -------
    list | None
        Query results when fetch=True, otherwise None.
    """

    with conn.cursor() as cursor:
        cursor.execute(query, params)

        if fetch:
            return cursor.fetchall()

        return None

def fetch_in_batches(conn, query, batch_size=10000):
    with conn.cursor() as cursor:
        cursor.execute(query)

        while True:
            rows = cursor.fetchmany(batch_size)

            if not rows:
                break

            yield rows

def table_exists(conn, schema_name, table_name):
    """
    Check whether a table exists in a PostgreSQL schema.

    Example:
        table_exists(conn, "public", "customer")
    """

    query = """
        SELECT EXISTS (
            SELECT 1
            FROM information_schema.tables
            WHERE table_schema = %s
              AND table_name = %s
        );
    """

    result = execute_query(
        conn,
        query,
        (schema_name, table_name),
        fetch=True
    )

    return result[0][0]


def get_table_schema(conn, schema_name, table_name):
    """
    Retrieve the column information for a target table.

    Returns a list of dictionaries containing:
        column_name
        data_type
        is_nullable
        column_default
    """

    query = """
        SELECT
            column_name,
            data_type,
            is_nullable,
            column_default
        FROM information_schema.columns
        WHERE table_schema = %s
          AND table_name = %s
        ORDER BY ordinal_position;
    """

    rows = execute_query(
        conn,
        query,
        (schema_name, table_name),
        fetch=True
    )

    return [
        {
            "column_name": row[0],
            "data_type": row[1],
            "is_nullable": row[2],
            "column_default": row[3]
        }
        for row in rows
    ]


def record_exists(conn, schema_name, table_name, identity_column, identity_value):
    """
    Check whether a record already exists in a table.

    Example:
        record_exists(
            conn,
            "public",
            "customer",
            "email",
            "john@example.com"
        )

    Returns
    -------
    bool
        True if a matching record exists.
        False otherwise.
    """

    query = sql.SQL("""
        SELECT EXISTS (
            SELECT 1
            FROM {}.{}
            WHERE {} = %s
        );
    """).format(
        sql.Identifier(schema_name),
        sql.Identifier(table_name),
        sql.Identifier(identity_column)
    )

    with conn.cursor() as cursor:
        cursor.execute(query, (identity_value,))
        return cursor.fetchone()[0]


def generate_uuid():
    """
    Generate a UUID for entities that require a GUID.
    """
    return uuid.uuid4()

def create_deterministic_faker(seed_value): 
    """ Creates a Faker instance whose output is deterministic for the supplied source value. """ 
    seed = int( hashlib.sha256( str(seed_value).encode("utf-8") ).hexdigest(), 16 ) 
    fake = Faker() 
    fake.seed_instance(seed) 
    
    return fake


def insert_record(conn, schema_name, table_name, data):
    """
    Insert a single record into a PostgreSQL table.

    Parameters
    ----------
    conn : psycopg connection

    schema_name : str
        Target schema.

    table_name : str
        Target table.

    data : dict
        Dictionary where:
            key   = column name
            value = value to insert

    Example
    -------
        insert_record(
            conn,
            "public",
            "customer",
            {
                "customer_guid": generate_uuid(),
                "first_name": "John",
                "last_name": "Doe",
                "email": "john@example.com",
                "status": "ACTIVE"
            }
        )
    """

    if not data:
        raise ValueError("Cannot insert an empty record.")

    columns = list(data.keys())
    values = list(data.values())

    column_identifiers = [
        sql.Identifier(column)
        for column in columns
    ]

    placeholders = sql.SQL(", ").join(
        sql.Placeholder() for _ in values
    )

    query = sql.SQL("""
        INSERT INTO {}.{} ({})
        VALUES ({})
    """).format(
        sql.Identifier(schema_name),
        sql.Identifier(table_name),
        sql.SQL(", ").join(column_identifiers),
        placeholders
    )

    with conn.cursor() as cursor:
        cursor.execute(query, values)


def insert_records(
    conn,
    schema_name,
    table_name,
    records,
    conflict_columns
):
    """
    Insert multiple records using the same target table.

    Supports both:
        conflict_columns="email"

    and composite conflict keys:
        conflict_columns=["fk_customer_id", "fk_device_id"]
    """

    if not records:
        return

    if isinstance(conflict_columns, str):
        conflict_columns = [conflict_columns]

    columns = list(records[0].keys())

    column_identifiers = [
        sql.Identifier(column)
        for column in columns
    ]

    conflict_identifiers = [
        sql.Identifier(column)
        for column in conflict_columns
    ]

    placeholders = sql.SQL(", ").join(
        sql.Placeholder() for _ in columns
    )

    query = sql.SQL("""
        INSERT INTO {}.{} ({})
        VALUES ({})
        ON CONFLICT ({}) DO NOTHING
    """).format(
        sql.Identifier(schema_name),
        sql.Identifier(table_name),
        sql.SQL(", ").join(column_identifiers),
        placeholders,
        sql.SQL(", ").join(conflict_identifiers)
    )

    values = [
        tuple(record[column] for column in columns)
        for record in records
    ]

    with conn.cursor() as cursor:
        cursor.executemany(query, values)

def generate_missing_customer_field(column_name, seed_value):
    """
    Generates a value for a missing customer field.

    Gender is used as the source of truth so that
    title and first name remain consistent.
    """

    fake = create_deterministic_faker(seed_value)

    rng = random.Random(str(seed_value))

    # Generate gender once for this customer
    gender = rng.choice(["MALE", "FEMALE"])

    generators = {
        "customer_guid": lambda: uuid.uuid5(
            uuid.NAMESPACE_DNS,
            str(seed_value)
        ),

        "customer_title": lambda: (
            "Mr" if gender == "MALE"
            else rng.choice(["Ms", "Mrs"])
        ),

        "first_name": lambda: (
            fake.first_name_male()
            if gender == "MALE"
            else fake.first_name_female()
        ),

        "last_name": lambda: fake.last_name(),

        "date_of_birth": lambda: fake.date_of_birth(
            minimum_age=18,
            maximum_age=80
        ),

        "gender": lambda: gender,

        "country_of_origin": lambda: fake.country(),

        "status": lambda: "ACTIVE",
    }

    generator = generators.get(column_name)

    if generator is None:
        return None

    return generator()

def generate_missing_account_field(column_name, seed_value):
    """
    Generates a value for a missing account field.

    Returns None if the field should be handled by the
    database or requires a different mapping/business rule.
    """

    fake = create_deterministic_faker(seed_value)

    generators = {
        "account_guid": lambda: uuid.uuid5(
            uuid.NAMESPACE_DNS,
            str(seed_value)
        ),

        "status": lambda: "ACTIVE",

        "balance": lambda: 0.00,
    }

    generator = generators.get(column_name)

    if generator is None:
        return None

    return generator()

def generate_missing_device_field(column_name, seed_value):
    """
    Generates values for device fields that are not supplied
    by the source data.
    """

    generators = {
        "device_guid": lambda: uuid.uuid5(
            uuid.NAMESPACE_DNS,
            f"device:{seed_value}"
        )
    }

    generator = generators.get(column_name)

    if generator is None:
        return None

    return generator()

def load_customer(conn):
    schema_name = "public"
    table_name = "customer"
    print("CUSTOMER LOAD")

    # 1. Check target table exists
    if not table_exists(conn, schema_name, table_name):
        raise RuntimeError(
            f"Target table {schema_name}.{table_name} does not exist."
        )

    print(f"Target table found: {schema_name}.{table_name}")


    # 2. Get target table schema
    target_schema = get_table_schema(
        conn,
        schema_name,
        table_name
    )

    target_columns = {
        column["column_name"]: column
        for column in target_schema
    }

    # 3. Run customer migration SQL
    migration_sql = """
        SELECT DISTINCT
            email_address,
            billing_street,
            billing_city,
            billing_region,
            billing_country,
            billing_postal_code,
            mobile_phone_number
        FROM raw.iovation
        WHERE email_address IS NOT NULL;
    """
    customer_rows = []

    for source_rows in fetch_in_batches(
        conn,
        migration_sql,
        batch_size=10000
    ):

        print(f"\nMigration returned {len(source_rows)} rows.")


        source_columns = [
            "email_address",
            "billing_street",
            "billing_city",
            "billing_region",
            "billing_country",
            "billing_postal_code",
            "mobile_phone_number"
        ]


        # 4. Determine target columns that are not supplied by the migration

        missing_columns = [
            column
            for column in target_columns
            if column not in source_columns
        ]

        print("\nTarget columns not supplied by migration:")

        for column in missing_columns:
            column_info = target_columns[column]

            print(
                f"  - {column} "
                f"(type={column_info['data_type']}, "
                f"nullable={column_info['is_nullable']}, "
                f"default={column_info['column_default']})"
            )

        # 5. Generate missing fields for each source row
        
        for row in source_rows:

            source_data = dict(
                zip(source_columns, row)
            )

            # Use a stable source value as the generation seed.
            seed_value = source_data["email_address"]

            # Mapping from source → target
                
            customer = {
                "customer_guid": generate_missing_customer_field(
                    "customer_guid",
                    seed_value
                ),

                "customer_title": generate_missing_customer_field(
                    "customer_title",
                    seed_value
                ),

                "first_name": generate_missing_customer_field(
                    "first_name",
                    seed_value
                ),

                "last_name": generate_missing_customer_field(
                    "last_name",
                    seed_value
                ),

                "date_of_birth": generate_missing_customer_field(
                    "date_of_birth",
                    seed_value
                ),

                "email": source_data["email_address"],

                "cellphone": source_data["mobile_phone_number"],

                "gender": generate_missing_customer_field(
                    "gender",
                    seed_value
                ),

                "country": source_data["billing_country"],

                "country_of_origin": generate_missing_customer_field(
                    "country_of_origin",
                    seed_value
                ).upper(),

                "status": generate_missing_customer_field(
                    "status",
                    seed_value
                )
            }
            customer_rows.append(customer)

        
        xprint("\nCUSTOMER ROWS TO BE INSERTED")
        xprint("----------------------------")

        for index, customer in enumerate(customer_rows, start=1):

            xprint(f"\nCustomer {index}:")

            for column, value in customer.items():
                xprint(f"  {column}: {value}")
      
    return customer_rows


def load_account(conn):
    schema_name = "public"
    table_name = "account"

    print("ACCOUNT LOAD")

    if not table_exists(conn, schema_name, table_name):
        raise RuntimeError(
            f"Target table {schema_name}.{table_name} does not exist."
        )

    print(f"Target table found: {schema_name}.{table_name}")

    target_schema = get_table_schema(
        conn,
        schema_name,
        table_name
    )

    target_columns = {
        column["column_name"]: column
        for column in target_schema
    }

    # PostgreSQL resolves the customer FK using a JOIN.
    migration_sql = """
        SELECT DISTINCT
            r.account_code,
            r.email_address,
            c.id AS customer_id
        FROM raw.iovation r
        JOIN public.customer c
            ON c.email = r.email_address
        WHERE r.account_code IS NOT NULL;
    """

    source_columns = [
        "account_code",
        "email_address",
        "customer_id"
    ]

    account_rows = []
    
    for source_rows in fetch_in_batches(
        conn,
        migration_sql,
        batch_size=10000
    ):

        print(f"\nMigration returned {len(source_rows)} rows.")

        missing_columns = [
            column
            for column in target_columns
            if column not in source_columns
        ]

        print("\nTarget columns not supplied by migration:")

        for column in missing_columns:
            column_info = target_columns[column]

            print(
                f"  - {column} "
                f"(type={column_info['data_type']}, "
                f"nullable={column_info['is_nullable']}, "
                f"default={column_info['column_default']})"
            )

        

        for row in source_rows:

            source_data = dict(
                zip(source_columns, row)
            )

            seed_value = source_data["account_code"]

            account = {
                "account_guid": generate_missing_account_field(
                    "account_guid",
                    seed_value
                ),

                "fk_customer_id": source_data["customer_id"],

                "status": generate_missing_account_field(
                    "status",
                    seed_value
                ),

                "balance": generate_missing_account_field(
                    "balance",
                    seed_value
                ),

                "src_account_code": source_data["account_code"]
            }

            account_rows.append(account)

        xprint("\nACCOUNT ROWS TO BE INSERTED")
        xprint("---------------------------")

        for index, account in enumerate(account_rows, start=1):

            xprint(f"\nAccount {index}:")

            for column, value in account.items():
                xprint(f"  {column}: {value}")

    return account_rows
       
def load_device(conn):
    schema_name = "network"
    table_name = "device"

    print("DEVICE LOAD")

    if not table_exists(conn, schema_name, table_name):
        raise RuntimeError(
            f"Target table {schema_name}.{table_name} does not exist."
        )

    print(f"Target table found: {schema_name}.{table_name}")

    target_schema = get_table_schema(
        conn,
        schema_name,
        table_name
    )

    target_columns = {
        column["column_name"]: column
        for column in target_schema
    }

    migration_sql = """
        SELECT DISTINCT
            device_id,
            device_type,
            operating_system,
            browser_type,
            browser_version,
            browser_language,
            screen_resolution,
            device_manufacturer,
            device_brand_name,
            device_language
        FROM raw.iovation
        WHERE device_id IS NOT NULL;
    """

    source_columns = [
        "device_id",
        "device_type",
        "operating_system",
        "browser_type",
        "browser_version",
        "browser_language",
        "screen_resolution",
        "device_manufacturer",
        "device_brand_name",
        "device_language"
    ]

    device_rows = []

    for source_rows in fetch_in_batches(
        conn,
        migration_sql,
        batch_size=10000
    ):

        print(f"\nMigration returned {len(source_rows)} rows.")

        for row in source_rows:

            source_data = dict(
                zip(source_columns, row)
            )

            source_device_id = source_data["device_id"]

            device = {
                "device_guid": generate_missing_device_field(
                    "device_guid",
                    source_device_id
                ),

                "source_device_id": source_device_id,

                "device_type": source_data["device_type"],

                "operating_system": source_data["operating_system"],

                "browser_type": source_data["browser_type"],

                "browser_version": source_data["browser_version"],

                "browser_language": source_data["browser_language"],

                "screen_resolution": source_data["screen_resolution"],

                "device_manufacturer": source_data[
                    "device_manufacturer"
                ],

                "device_brand_name": source_data[
                    "device_brand_name"
                ],

                # Not available in raw.iovation
                "model_id": None,

                "device_language": source_data[
                    "device_language"
                ]
            }

            device_rows.append(device)

    xprint("\nDEVICE ROWS TO BE INSERTED")
    xprint("-------------------------")

    for index, device in enumerate(device_rows, start=1):

        xprint(f"\nDevice {index}:")

        for column, value in device.items():
            xprint(f"  {column}: {value}")

    return device_rows

def load_customer_device(conn):
    schema_name = "network"
    table_name = "customer_device"

    print("CUSTOMER DEVICE LOAD")

    if not table_exists(conn, schema_name, table_name):
        raise RuntimeError(
            f"Target table {schema_name}.{table_name} does not exist."
        )

    migration_sql = """
        SELECT
            r.email_address,
            r.device_id,
            MIN(r.event_timestamp) AS first_seen,
            MAX(r.event_timestamp) AS last_seen,
            BOOL_OR(
                CASE
                    WHEN LOWER(r.new_device) IN ('true', 'yes', '1')
                        THEN TRUE
                    WHEN LOWER(r.new_device) IN ('false', 'no', '0')
                        THEN FALSE
                    ELSE NULL
                END
            ) AS is_new_device
        FROM raw.iovation r
        WHERE r.email_address IS NOT NULL
          AND r.device_id IS NOT NULL
        GROUP BY
            r.email_address,
            r.device_id;
    """

    source_columns = [
        "email_address",
        "device_id",
        "first_seen",
        "last_seen",
        "is_new_device"
    ]

    customer_device_rows = []

    for source_rows in fetch_in_batches(
        conn,
        migration_sql,
        batch_size=10000
    ):

        print(
            f"\nMigration returned "
            f"{len(source_rows)} customer-device rows."
        )

        for row in source_rows:

            source_data = dict(
                zip(source_columns, row)
            )

            # PostgreSQL resolves BOTH foreign keys.
            mapping_sql = """
                SELECT
                    c.id AS customer_id,
                    d.id AS device_id
                FROM public.customer c
                JOIN network.device d
                    ON d.source_device_id = %s
                WHERE c.email = %s;
            """

            mapping = execute_query(
                conn,
                mapping_sql,
                (
                    source_data["device_id"],
                    source_data["email_address"]
                ),
                fetch=True
            )

            if not mapping:
                xprint(
                    "Could not map customer/device: "
                    f"{source_data['email_address']} / "
                    f"{source_data['device_id']}"
                )
                continue

            customer_id, device_id = mapping[0]

            customer_device = {
                "fk_customer_id": customer_id,
                "fk_device_id": device_id,
                "first_seen": source_data["first_seen"],
                "last_seen": source_data["last_seen"],
                "is_new_device": source_data["is_new_device"]
            }

            customer_device_rows.append(customer_device)

    xprint("\nCUSTOMER DEVICE ROWS TO BE INSERTED")
    xprint("----------------------------------")

    for index, row in enumerate(
        customer_device_rows,
        start=1
    ):

        xprint(f"\nCustomer Device {index}:")

        for column, value in row.items():
            xprint(f"  {column}: {value}")

    return customer_device_rows

def load_iovation_event(conn):
    schema_name = "network"
    table_name = "iovation_event"

    print("IOVATION EVENT LOAD")

    if not table_exists(conn, schema_name, table_name):
        raise RuntimeError(
            f"Target table {schema_name}.{table_name} does not exist."
        )

    print(f"Target table found: {schema_name}.{table_name}")

    migration_sql = """
        SELECT
            r.id AS source_iovation_id,

            c.id AS customer_id,

            d.id AS device_id,

            r.integration_point,
            r.tracking_number,
            r.event_id,
            r.result,
            r.score,
            r.matched_rules,
            r.real_ip_address,
            r.stated_ip_address,
            r.real_ip_city,
            r.real_ip_region,
            r.real_ip_country,
            r.stated_city AS stated_ip_city,
            r.stated_region AS stated_ip_region,
            r.stated_country AS stated_ip_country,
            r.real_ip_proxy_type,
            r.stated_ip_proxy_type,
            r.monetary_amount,

            CASE
                WHEN LOWER(r.new_device) IN ('true', 'yes', '1')
                    THEN TRUE

                WHEN LOWER(r.new_device) IN ('false', 'no', '0')
                    THEN FALSE

                ELSE NULL
            END AS is_new_device,

            r.event_timestamp AS observed_at

        FROM raw.iovation r

        JOIN public.customer c
            ON c.email = r.email_address

        JOIN network.device d
            ON d.source_device_id = r.device_id;
    """

    source_columns = [
        "source_iovation_id",
        "customer_id",
        "device_id",
        "integration_point",
        "tracking_number",
        "event_id",
        "result",
        "score",
        "matched_rules",
        "real_ip_address",
        "stated_ip_address",
        "real_ip_city",
        "real_ip_region",
        "real_ip_country",
        "stated_ip_city",
        "stated_ip_region",
        "stated_ip_country",
        "real_ip_proxy_type",
        "stated_ip_proxy_type",
        "monetary_amount",
        "is_new_device",
        "observed_at"
    ]

    iovation_event_rows = []

    for source_rows in fetch_in_batches(
        conn,
        migration_sql,
        batch_size=10000
    ):

        print(
            f"\nMigration returned "
            f"{len(source_rows)} iovation events."
        )

        for row in source_rows:

            source_data = dict(
                zip(source_columns, row)
            )

            source_iovation_id = source_data[
                "source_iovation_id"
            ]

            iovation_event = {
                "iovation_event_guid": uuid.uuid5(
                    uuid.NAMESPACE_DNS,
                    f"iovation-event:{source_iovation_id}"
                ),

                "fk_customer_id": source_data[
                    "customer_id"
                ],

                "fk_device_id": source_data[
                    "device_id"
                ],

                "integration_point": source_data[
                    "integration_point"
                ],
                

                "tracking_number": source_data[
                    "tracking_number"
                ],

                "event_id": source_data[
                    "event_id"
                ],

                "result": source_data[
                    "result"
                ],

                "score": source_data[
                    "score"
                ],

                "matched_rules": source_data[
                    "matched_rules"
                ],

                "real_ip_address": source_data[
                    "real_ip_address"
                ],

                "stated_ip_address": source_data[
                    "stated_ip_address"
                ],

                "real_ip_city": source_data[
                    "real_ip_city"
                ],

                "real_ip_region": source_data[
                    "real_ip_region"
                ],

                "real_ip_country": source_data[
                    "real_ip_country"
                ],

                "stated_ip_city": source_data[
                    "stated_ip_city"
                ],

                "stated_ip_region": source_data[
                    "stated_ip_region"
                ],

                "stated_ip_country": source_data[
                    "stated_ip_country"
                ],

                "real_ip_proxy_type": source_data[
                    "real_ip_proxy_type"
                ],

                "stated_ip_proxy_type": source_data[
                    "stated_ip_proxy_type"
                ],

                "monetary_amount": source_data[
                    "monetary_amount"
                ],

                "is_new_device": source_data[
                    "is_new_device"
                ],

                "observed_at": source_data[
                    "observed_at"
                ]
            }

            iovation_event_rows.append(
                iovation_event
            )

    xprint("\nIOVATION EVENT ROWS TO BE INSERTED")
    xprint("---------------------------------")

    for index, event in enumerate(
        iovation_event_rows,
        start=1
    ):

        xprint(f"\nIovation Event {index}:")

        for column, value in event.items():
            xprint(f"  {column}: {value}")

    return iovation_event_rows

def load_financial_transaction(conn):
    schema_name = "public"
    table_name = "financial_transaction"

    print("FINANCIAL TRANSACTION LOAD")

    if not table_exists(conn, schema_name, table_name):
        raise RuntimeError(
            f"Target table {schema_name}.{table_name} does not exist."
        )

    print(f"Target table found: {schema_name}.{table_name}")

    migration_sql = """
        SELECT
            a.id AS account_id,
            a.fk_customer_id AS customer_id,

            r.event_timestamp,
            r.monetary_amount,
            r.currency_type,
            r.credit_card_bin,
            r.transaction_field_tu_billing_id

        FROM raw.iovation r

        JOIN public.account a
            ON a.src_account_code = r.account_code

        WHERE r.monetary_amount IS NOT NULL
          AND r.integration_point = 'deposits';
    """

    source_columns = [
        "account_id",
        "customer_id",
        "event_timestamp",
        "monetary_amount",
        "currency_type",
        "credit_card_bin",
        "transaction_field_tu_billing_id"
    ]

    transaction_types = [
        "EFT Deposit",
        "Credit Card Deposit",
        "Online Deposit"
    ]

    financial_transaction_rows = []

    for source_rows in fetch_in_batches(
        conn,
        migration_sql,
        batch_size=10000
    ):
        print(
            f"\nMigration returned "
            f"{len(source_rows)} financial transactions."
        )

        for row in source_rows:
            source_data = dict(zip(source_columns, row))

            # Deterministic mock transaction type
            rng = random.Random(
                str(source_data["transaction_field_tu_billing_id"])
                + str(source_data["event_timestamp"])
                + str(source_data["account_id"])
            )

            transaction_type_name = rng.choice(transaction_types)

            # Look up the actual database ID for the generated type
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT id
                    FROM public.customer_transaction_type
                    WHERE transaction_type_name = %s
                    """,
                    (transaction_type_name,)
                )

                transaction_type_id = cursor.fetchone()[0]

            transaction_seed = (
                f"financial-transaction:"
                f"{source_data['account_id']}:"
                f"{source_data['event_timestamp']}:"
                f"{source_data['monetary_amount']}:"
                f"{source_data['transaction_field_tu_billing_id']}"
            )

            transaction = {
                "transaction_guid": uuid.uuid5(
                    uuid.NAMESPACE_DNS,
                    transaction_seed
                ),
                "fk_customer_id": source_data["customer_id"],
                "fk_transaction_type_id": transaction_type_id,
                "fk_account_id": source_data["account_id"],
                "transaction_amount": source_data["monetary_amount"],
                "tax_rate": None,
                "balance": None,
                "reference_comment": (
                    source_data["transaction_field_tu_billing_id"]
                ),
                "reason": "DEPOSIT",
                "is_cancelled": False,
                "is_paid_out": False,
                "transaction_timestamp": (
                    source_data["event_timestamp"]
                )
            }

            financial_transaction_rows.append(transaction)

    xprint("\nFINANCIAL TRANSACTION ROWS TO BE INSERTED")
    xprint("------------------------------------------")

    for index, transaction in enumerate(
        financial_transaction_rows,
        start=1
    ):
        xprint(f"\nFinancial Transaction {index}:")

        for column, value in transaction.items():
            xprint(f"  {column}: {value}")

    return financial_transaction_rows


def main():
    print("Normalized load pipeline starting...")

    conn = get_pg_connection()

    if conn is None:
        return

    try:
        
        # CUSTOMER
        customer_rows = load_customer(conn)
        insert_records(conn, "public", "customer", customer_rows, "email")
        conn.commit()

        # ACCOUNT
        account_rows = load_account(conn)
        insert_records(conn, "public", "account", account_rows, "src_account_code")
        conn.commit()

        # DEVICE
        device_rows = load_device(conn)
        insert_records(conn, "network", "device", device_rows, "source_device_id")
        conn.commit()
        
        # CUSTOMER DEVICE
        customer_device_rows = load_customer_device(conn)
        insert_records(conn, "network", "customer_device", customer_device_rows, ["fk_customer_id", "fk_device_id"])
        conn.commit()
        
        # IOVATION EVENT
        iovation_event_rows = load_iovation_event(conn)
        insert_records(conn, "network", "iovation_event", iovation_event_rows, "iovation_event_guid")
        conn.commit()

        # FINANCIAL TRANSACTION
        financial_transaction_rows = load_financial_transaction(conn)
        insert_records(conn, "public", "financial_transaction", financial_transaction_rows, "transaction_guid")
        conn.commit()
        

    except Exception as e:
        conn.rollback()
        print(f"\nPipeline failed: {e}")
        raise

    finally:
        conn.close()
        print("\nPostgreSQL connection closed.")



if __name__ == "__main__":
    main()

