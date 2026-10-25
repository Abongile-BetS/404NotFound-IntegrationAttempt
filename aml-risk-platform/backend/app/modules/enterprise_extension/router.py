"""Additive AML/KYC intelligence endpoints over 404NotFound existing PostgreSQL schema.
No independent customer database, no simulated production results.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from app.shared.auth.dependencies import get_current_user
from app.shared.database.connection import fetch_all, fetch_one

router = APIRouter(prefix="/intelligence", tags=["AML/KYC Intelligence Extension"], dependencies=[Depends(get_current_user)])

MODULES = {
    "aml": ("AML Monitoring", "Financial activity and recorded risk events"),
    "kyc": ("KYC & CDD", "Identity and verification status"),
    "media": ("Adverse Media", "Recorded media screening results; live retrieval not connected"),
    "screening": ("PEP & Sanctions", "Potential matches require analyst confirmation"),
    "network": ("Network Intelligence", "Shared customer-device relationships"),
    "rules": ("Rule Management", "Existing configured rules and versions"),
    "risk": ("AML Risk Evaluation", "Persisted customer risk assessments"),
    "geography": ("Geographic Intelligence", "Customer country distribution"),
    "reports": ("AI Reports", "Evidence-backed report data; LLM generation not connected"),
}

SQL = {
 "aml": """SELECT c.customer_guid::text AS id, concat_ws(' ',c.first_name,c.last_name) AS customer, re.event_type AS finding, re.severity AS status, re.detected_at::text AS date FROM risk.risk_event re JOIN public.customer c ON c.id=re.fk_customer_id ORDER BY re.detected_at DESC NULLS LAST LIMIT :limit""",
 "kyc": """SELECT c.customer_guid::text AS id, concat_ws(' ',c.first_name,c.last_name) AS customer, COALESCE(k.identity_status,'NOT_CHECKED') AS identity, COALESCE(k.address_status,'NOT_CHECKED') AS address, COALESCE(k.verification_result,'NOT_ASSESSED') AS status FROM public.customer c LEFT JOIN LATERAL (SELECT * FROM public.kyc_record WHERE fk_customer_id=c.id ORDER BY id DESC LIMIT 1) k ON TRUE ORDER BY c.created_at DESC LIMIT :limit""",
 "media": """SELECT c.customer_guid::text AS id, concat_ws(' ',c.first_name,c.last_name) AS customer, s.matched_entity AS finding, COALESCE(s.result,'UNKNOWN') AS status, s.screened_at::text AS date FROM public.screening_result s JOIN public.customer c ON c.id=s.fk_customer_id WHERE lower(s.screening_type) LIKE '%media%' ORDER BY s.screened_at DESC NULLS LAST LIMIT :limit""",
 "screening": """SELECT c.customer_guid::text AS id, concat_ws(' ',c.first_name,c.last_name) AS customer, s.screening_type AS type, s.matched_entity AS finding, COALESCE(s.result,'UNKNOWN') AS status, s.screened_at::text AS date FROM public.screening_result s JOIN public.customer c ON c.id=s.fk_customer_id WHERE lower(s.screening_type) LIKE '%pep%' OR lower(s.screening_type) LIKE '%sanction%' ORDER BY s.screened_at DESC NULLS LAST LIMIT :limit""",
 "network": """SELECT d.device_guid::text AS id, COUNT(DISTINCT cd.fk_customer_id) AS linked_customers, d.device_type AS type FROM public.customer_device cd JOIN public.device d ON d.id=cd.fk_device_id GROUP BY d.id,d.device_guid,d.device_type HAVING COUNT(DISTINCT cd.fk_customer_id)>1 ORDER BY linked_customers DESC LIMIT :limit""",
 "rules": """SELECT code AS id, name, category, severity AS status, risk_weight AS weight, enabled, version FROM risk.rules ORDER BY category,code LIMIT :limit""",
 "risk": """SELECT c.customer_guid::text AS id, concat_ws(' ',c.first_name,c.last_name) AS customer, rs.score, rs.risk_level AS status, rs.model_version AS version, rs.calculated_at::text AS date FROM public.customer c JOIN LATERAL (SELECT * FROM risk.risk_score WHERE fk_customer_id=c.id ORDER BY calculated_at DESC NULLS LAST,id DESC LIMIT 1) rs ON TRUE ORDER BY rs.score DESC NULLS LAST LIMIT :limit""",
 "geography": """SELECT COALESCE(NULLIF(country,''),'Unknown') AS country, COUNT(*) AS customers, COUNT(*) FILTER (WHERE customer_fica_compliant) AS fica_compliant FROM public.customer GROUP BY 1 ORDER BY customers DESC LIMIT :limit""",
 "reports": """SELECT c.customer_guid::text AS id, concat_ws(' ',c.first_name,c.last_name) AS customer, rs.score, rs.risk_level AS status, rs.calculated_at::text AS date FROM public.customer c JOIN LATERAL (SELECT * FROM risk.risk_score WHERE fk_customer_id=c.id ORDER BY calculated_at DESC NULLS LAST,id DESC LIMIT 1) rs ON TRUE ORDER BY rs.calculated_at DESC NULLS LAST LIMIT :limit""",
}

@router.get('/modules')
async def modules():
    return [{"key": k, "title": v[0], "description": v[1]} for k,v in MODULES.items()]

@router.get('/{module}')
async def list_module(module: str, limit: int=Query(default=100,ge=1,le=500)):
    if module not in MODULES:
        raise HTTPException(404, "Unknown intelligence module")
    try:
        rows=await fetch_all(SQL[module], {"limit":limit})
    except Exception as exc:
        # Do not expose database credentials or SQL details.
        raise HTTPException(503, "Module data unavailable: check database schema and migrations") from exc
    return {"module":module,"title":MODULES[module][0],"description":MODULES[module][1],"count":len(rows),"rows":rows,"source":"404NotFound PostgreSQL", "synthetic":False}

@router.get('/reports/customer/{customer_id}')
async def report_evidence(customer_id: str):
    try:
        customer=await fetch_one("SELECT customer_guid::text AS id, first_name, last_name, country, customer_fica_compliant FROM public.customer WHERE customer_guid::text=:id",{"id":customer_id})
        if not customer: raise HTTPException(404,"Customer not found")
        risk=await fetch_one("SELECT score,risk_level,scoring_method,model_version,calculated_at::text AS calculated_at FROM risk.risk_score WHERE fk_customer_id=(SELECT id FROM public.customer WHERE customer_guid::text=:id) ORDER BY calculated_at DESC NULLS LAST,id DESC LIMIT 1",{"id":customer_id})
        checks=await fetch_all("SELECT screening_type,result,match_found,screened_at::text AS screened_at FROM public.screening_result WHERE fk_customer_id=(SELECT id FROM public.customer WHERE customer_guid::text=:id) ORDER BY screened_at DESC NULLS LAST LIMIT 20",{"id":customer_id})
        return {"customer":customer,"risk":risk,"screening":checks,"ai_generated":False,"note":"Evidence packet only; no LLM has been invoked."}
    except HTTPException: raise
    except Exception as exc: raise HTTPException(503,"Report evidence unavailable") from exc
