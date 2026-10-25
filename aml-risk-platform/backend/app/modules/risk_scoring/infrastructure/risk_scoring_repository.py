from app.shared.database.connection import fetch_all, fetch_one


class RiskScoringRepository:
    async def get_by_customer_id(self, customer_id: str):
        score = await fetch_one(
            """
            SELECT
                c.customer_guid::text AS customer_id,
                rs.score,
                rs.risk_level,
                rs.scoring_method,
                rs.model_version,
                rs.calculated_at::text AS calculated_at
            FROM risk.risk_score AS rs
            JOIN public.customer AS c ON c.id = rs.fk_customer_id
            WHERE c.customer_guid::text = :customer_id
            ORDER BY rs.calculated_at DESC NULLS LAST, rs.id DESC
            LIMIT 1
            """,
            {"customer_id": customer_id},
        )
        if score is None:
            return None

        score["risk_events"] = await fetch_all(
            """
            SELECT
                rules.category AS risk_category,
                re.event_type AS risk_type,
                rr.risk_points AS contribution,
                rr.evidence_json::text AS description,
                re.severity,
                re.status,
                re.detected_at::text AS detected_at
            FROM risk.risk_event AS re
            JOIN public.customer AS c ON c.id = re.fk_customer_id
            LEFT JOIN risk.rule_result AS rr ON rr.id = re.fk_rule_result_id
            LEFT JOIN risk.rules ON rules.id = rr.fk_rule_id
            WHERE c.customer_guid::text = :customer_id
            ORDER BY re.detected_at DESC, re.id DESC
            """,
            {"customer_id": customer_id},
        )
        return score