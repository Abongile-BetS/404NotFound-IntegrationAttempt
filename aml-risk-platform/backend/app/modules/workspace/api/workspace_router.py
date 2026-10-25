from datetime import datetime, timezone

from fastapi import HTTPException

from app.shared.database.connection import fetch_all, fetch_one


_WORKSPACES = {
    "dashboard": {
        "title": "Home dashboard",
        "subtitle": "Monitor customers, risk scores, alerts, and transaction activity.",
        "table_title": "Customers with the latest recorded risk score",
        "columns": [
            {"key": "customer", "label": "Customer"},
            {"key": "score", "label": "Risk score"},
            {"key": "level", "label": "Risk level"},
            {"key": "updated", "label": "Calculated"},
        ],
        "query": """
            SELECT
                concat_ws(' ', c.first_name, c.last_name) AS customer,
                COALESCE(rs.score::text, 'Not scored') AS score,
                COALESCE(rs.risk_level, 'Not scored') AS level,
                COALESCE(rs.calculated_at::text, '—') AS updated,
                c.customer_guid::text AS id
            FROM public.customer AS c
            LEFT JOIN LATERAL (
                SELECT score, risk_level, calculated_at
                FROM risk.risk_score
                WHERE fk_customer_id = c.id
                ORDER BY calculated_at DESC NULLS LAST, id DESC
                LIMIT 1
            ) AS rs ON TRUE
            ORDER BY rs.score DESC NULLS LAST, c.created_at DESC
            LIMIT 20
        """,
        "trend_query": """
            SELECT transaction_timestamp::date::text AS label, COUNT(*) AS "primary"
            FROM public.financial_transaction
            GROUP BY transaction_timestamp::date
            ORDER BY transaction_timestamp::date DESC
            LIMIT 7
        """,
        "trend_title": "Financial transactions by date",
        "series_label": "Transactions",
        "side_title": "Database totals",
    },
    "screening": {
        "title": "Risk screening workspace",
        "subtitle": "Screening results recorded for platform customers.",
        "table_title": "Screening results",
        "columns": [
            {"key": "customer", "label": "Customer"},
            {"key": "source", "label": "Screening type"},
            {"key": "result", "label": "Result"},
            {"key": "screened_at", "label": "Screened at"},
        ],
        "query": """
            SELECT
                s.screening_guid::text AS id,
                concat_ws(' ', c.first_name, c.last_name) AS customer,
                COALESCE(s.screening_type, 'Unspecified') AS source,
                COALESCE(s.result, 'Unspecified') AS result,
                COALESCE(s.screened_at::text, '—') AS screened_at
            FROM public.screening_result AS s
            JOIN public.customer AS c ON c.id = s.fk_customer_id
            ORDER BY s.screened_at DESC NULLS LAST, s.id DESC
            LIMIT 20
        """,
        "trend_query": """
            SELECT screened_at::date::text AS label, COUNT(*) AS "primary"
            FROM public.screening_result
            WHERE screened_at IS NOT NULL
            GROUP BY screened_at::date
            ORDER BY screened_at::date DESC
            LIMIT 7
        """,
        "trend_title": "Screenings by date",
        "series_label": "Screenings",
        "side_title": "Screening totals",
    },
    "transactions": {
        "title": "Transaction monitoring",
        "subtitle": "Financial transactions from the configured ledger.",
        "table_title": "Financial transactions",
        "columns": [
            {"key": "transaction", "label": "Transaction"},
            {"key": "customer", "label": "Customer"},
            {"key": "type", "label": "Type"},
            {"key": "amount", "label": "Amount"},
            {"key": "timestamp", "label": "Timestamp"},
        ],
        "query": """
            SELECT
                t.transaction_guid::text AS id,
                t.transaction_guid::text AS transaction,
                concat_ws(' ', c.first_name, c.last_name) AS customer,
                tt.transaction_type_name AS type,
                t.transaction_amount::float AS amount,
                t.transaction_timestamp::text AS timestamp
            FROM public.financial_transaction AS t
            JOIN public.customer AS c ON c.id = t.fk_customer_id
            JOIN public.customer_transaction_type AS tt ON tt.id = t.fk_transaction_type_id
            ORDER BY t.transaction_timestamp DESC, t.id DESC
            LIMIT 20
        """,
        "trend_query": """
            SELECT transaction_timestamp::date::text AS label, COUNT(*) AS "primary"
            FROM public.financial_transaction
            GROUP BY transaction_timestamp::date
            ORDER BY transaction_timestamp::date DESC
            LIMIT 7
        """,
        "trend_title": "Transactions by date",
        "series_label": "Transactions",
        "side_title": "Ledger totals",
    },
    "kyc": {
        "title": "KYC monitoring",
        "subtitle": "Customer onboarding and verification records.",
        "table_title": "Onboarding records",
        "columns": [
            {"key": "customer", "label": "Applicant"},
            {"key": "email", "label": "Email"},
            {"key": "status", "label": "Onboarding status"},
            {"key": "created", "label": "Created"},
        ],
        "query": """
            SELECT
                co.onboarding_guid::text AS id,
                concat_ws(' ', co.first_name, co.last_name) AS customer,
                co.email,
                co.onboarding_status AS status,
                co.created_at::text AS created
            FROM public.customer_onboarding AS co
            ORDER BY co.created_at DESC, co.id DESC
            LIMIT 20
        """,
        "trend_query": """
            SELECT created_at::date::text AS label, COUNT(*) AS "primary"
            FROM public.customer_onboarding
            GROUP BY created_at::date
            ORDER BY created_at::date DESC
            LIMIT 7
        """,
        "trend_title": "Onboarding records by date",
        "series_label": "Onboarding records",
        "side_title": "Verification totals",
    },
    "network": {
        "title": "Network intelligence",
        "subtitle": "Customer-device associations and observed device events.",
        "table_title": "Observed device events",
        "columns": [
            {"key": "customer", "label": "Customer"},
            {"key": "device", "label": "Device"},
            {"key": "result", "label": "Result"},
            {"key": "observed", "label": "Observed"},
        ],
        "query": """
            SELECT
                e.iovation_event_guid::text AS id,
                concat_ws(' ', c.first_name, c.last_name) AS customer,
                d.source_device_id AS device,
                COALESCE(e.result, 'Unspecified') AS result,
                e.observed_at::text AS observed
            FROM network.iovation_event AS e
            JOIN public.customer AS c ON c.id = e.fk_customer_id
            JOIN network.device AS d ON d.id = e.fk_device_id
            ORDER BY e.observed_at DESC, e.id DESC
            LIMIT 20
        """,
        "trend_query": """
            SELECT observed_at::date::text AS label, COUNT(*) AS "primary"
            FROM network.iovation_event
            GROUP BY observed_at::date
            ORDER BY observed_at::date DESC
            LIMIT 7
        """,
        "trend_title": "Device events by date",
        "series_label": "Device events",
        "side_title": "Network totals",
    },
    "alerts": {
        "title": "Alert queue",
        "subtitle": "Alerts recorded from risk scoring.",
        "table_title": "Alerts",
        "columns": [
            {"key": "alert", "label": "Alert"},
            {"key": "customer", "label": "Customer"},
            {"key": "type", "label": "Type"},
            {"key": "severity", "label": "Severity"},
            {"key": "status", "label": "Status"},
            {"key": "created", "label": "Created"},
        ],
        "query": """
            SELECT
                a.alert_guid::text AS id,
                a.alert_guid::text AS alert,
                concat_ws(' ', c.first_name, c.last_name) AS customer,
                COALESCE(a.alert_type, 'Unspecified') AS type,
                COALESCE(a.severity, 'Unspecified') AS severity,
                COALESCE(a.status, 'Unspecified') AS status,
                COALESCE(a.created_at::text, '—') AS created
            FROM public.alert AS a
            JOIN public.customer AS c ON c.id = a.fk_customer_id
            ORDER BY a.created_at DESC NULLS LAST, a.id DESC
            LIMIT 20
        """,
        "trend_query": """
            SELECT created_at::date::text AS label, COUNT(*) AS "primary"
            FROM public.alert
            WHERE created_at IS NOT NULL
            GROUP BY created_at::date
            ORDER BY created_at::date DESC
            LIMIT 7
        """,
        "trend_title": "Alerts by date",
        "series_label": "Alerts",
        "side_title": "Alert totals",
    },
    "investigations": {
        "title": "Investigations",
        "subtitle": "No investigation or case table is defined in the database setup.",
        "table_title": "No investigation records",
        "columns": [],
        "query": None,
        "trend_query": None,
        "trend_title": "Investigation activity",
        "series_label": "Investigations",
        "side_title": "Case data unavailable",
    },
    "executive": {
        "title": "Executive dashboard",
        "subtitle": "Portfolio totals from configured customer, risk, alert, and transaction data.",
        "table_title": "Recorded risk levels",
        "columns": [
            {"key": "level", "label": "Risk level"},
            {"key": "customers", "label": "Customers scored"},
        ],
        "query": """
            SELECT
                COALESCE(risk_level, 'Unspecified') AS level,
                COUNT(*) AS customers,
                COALESCE(risk_level, 'Unspecified') AS id
            FROM risk.risk_score
            GROUP BY risk_level
            ORDER BY customers DESC, level
        """,
        "trend_query": """
            SELECT created_at::date::text AS label, COUNT(*) AS "primary"
            FROM public.alert
            WHERE created_at IS NOT NULL
            GROUP BY created_at::date
            ORDER BY created_at::date DESC
            LIMIT 7
        """,
        "trend_title": "Alerts by date",
        "series_label": "Alerts",
        "side_title": "Portfolio totals",
    },
}


async def get_workspace_data(module: str):
    workspace = _WORKSPACES.get(module)
    if workspace is None:
        raise HTTPException(status_code=404, detail="Workspace module not found")

    summary = await fetch_one(
        """
        SELECT
            (SELECT COUNT(*) FROM public.customer) AS customers,
            (SELECT COUNT(*) FROM risk.risk_score) AS scores,
            (SELECT COUNT(*) FROM risk.risk_score WHERE upper(risk_level) = 'HIGH') AS high_risk,
            (SELECT COUNT(*) FROM public.alert) AS alerts,
            (SELECT COUNT(*) FROM public.alert
             WHERE upper(COALESCE(status, '')) IN ('OPEN', 'IN_REVIEW', 'PENDING')) AS open_alerts,
            (SELECT COUNT(*) FROM public.financial_transaction) AS transactions,
            (SELECT COALESCE(SUM(transaction_amount), 0)
             FROM public.financial_transaction) AS transaction_amount,
            (SELECT COUNT(*) FROM public.kyc_record) AS kyc_records,
            (SELECT COUNT(*) FROM public.customer_onboarding) AS onboarding_records,
            (SELECT COUNT(*) FROM public.customer_onboarding
             WHERE upper(onboarding_status) IN ('PENDING', 'UNDER_REVIEW')) AS pending_onboarding,
            (SELECT COUNT(*) FROM public.screening_result) AS screenings,
            (SELECT COUNT(*) FROM public.screening_result WHERE match_found IS TRUE) AS screening_matches,
            (SELECT COUNT(*) FROM network.device) AS devices,
            (SELECT COUNT(*) FROM network.customer_device) AS device_links,
            (SELECT COUNT(*) FROM network.iovation_event) AS device_events
        """
    )
    if summary is None:
        raise RuntimeError("Unable to retrieve workspace totals")
    rows = await fetch_all(workspace["query"]) if workspace["query"] else []
    trend = await fetch_all(workspace["trend_query"]) if workspace["trend_query"] else []
    trend.reverse()
    latest_model = await fetch_one(
        """
        SELECT model_version
        FROM risk.risk_score
        WHERE model_version IS NOT NULL
        ORDER BY calculated_at DESC NULLS LAST, id DESC
        LIMIT 1
        """
    )
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")

    module_metrics = {
        "dashboard": [
            ("High-risk customers", summary["high_risk"]),
            ("Open alerts", summary["open_alerts"]),
            ("Transactions", summary["transactions"]),
            ("Transaction amount", float(summary["transaction_amount"])),
        ],
        "screening": [
            ("Screenings", summary["screenings"]),
            ("Matches", summary["screening_matches"]),
            ("Customers", summary["customers"]),
            ("Risk scores", summary["scores"]),
        ],
        "transactions": [
            ("Transactions", summary["transactions"]),
            ("Recorded amount", float(summary["transaction_amount"])),
            ("Customers", summary["customers"]),
            ("Open alerts", summary["open_alerts"]),
        ],
        "kyc": [
            ("Customers", summary["customers"]),
            ("KYC records", summary["kyc_records"]),
            ("Onboarding records", summary["onboarding_records"]),
            ("Pending onboarding", summary["pending_onboarding"]),
        ],
        "network": [
            ("Devices", summary["devices"]),
            ("Customer-device links", summary["device_links"]),
            ("Observed events", summary["device_events"]),
            ("Customers", summary["customers"]),
        ],
        "alerts": [
            ("Alerts", summary["alerts"]),
            ("Open alerts", summary["open_alerts"]),
            ("High-risk customers", summary["high_risk"]),
            ("Customers", summary["customers"]),
        ],
        "investigations": [
            ("Investigation records", 0),
            ("Alerts", summary["alerts"]),
            ("High-risk customers", summary["high_risk"]),
            ("Customers", summary["customers"]),
        ],
        "executive": [
            ("Customers", summary["customers"]),
            ("High-risk customers", summary["high_risk"]),
            ("Alerts", summary["alerts"]),
            ("Transactions", summary["transactions"]),
        ],
    }[module]
    colors = ("red", "amber", "blue", "white")
    metrics = [
        {
            "label": label,
            "value": str(value),
            "detail": "Recorded in the configured database",
            "tone": colors[index],
        }
        for index, (label, value) in enumerate(module_metrics)
    ]
    side_metrics = [
        {
            "label": label,
            "value": str(value),
            "detail": "Recorded in the configured database",
            "tone": colors[index],
        }
        for index, (label, value) in enumerate(module_metrics)
    ]

    return {
        "title": workspace["title"],
        "subtitle": workspace["subtitle"],
        "updated_at": now,
        "last_sync": now,
        "model_version": (latest_model or {}).get("model_version") or "Not available",
        "demo": False,
        "organization": {
            "name": "AML Risk Platform",
            "description": "PostgreSQL-backed operational data",
        },
        "analyst": {"name": "System", "role": "Database", "initials": "DB"},
        "alert_count": str(summary["alerts"]),
        "kpis": metrics,
        "trend_title": workspace["trend_title"],
        "trend": trend,
        "series": [
            {"key": "primary", "label": workspace["series_label"], "color": "#62a5ff"}
        ],
        "table_title": workspace["table_title"],
        "columns": workspace["columns"],
        "rows": rows,
        "side_title": workspace["side_title"],
        "side_metrics": side_metrics,
        "view": {},
    }
