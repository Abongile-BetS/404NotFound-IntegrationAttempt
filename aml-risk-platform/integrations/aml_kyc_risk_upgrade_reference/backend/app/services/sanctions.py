from dataclasses import dataclass
from datetime import datetime, timezone
from difflib import SequenceMatcher
import re
import ssl
from xml.etree import ElementTree

import httpx
import truststore


OFFICIAL_SOURCES = (
    (
        "South Africa FIC TFS",
        "https://transfer.fic.gov.za/public/folder/SE-MPQpJlUKmxgfA11NwZQ/Downloads/Consolidated%20United%20Nations%20Security%20Council%20Sanctions%20List.xml",
        "https://tfs.fic.gov.za/Pages/DownLoadList",
    ),
    (
        "UN Security Council Consolidated List",
        "https://scsanctions.un.org/resources/xml/en/name/consolidated.xml",
        "https://main.un.org/securitycouncil/en/content/un-sc-consolidated-list",
    ),
)


@dataclass
class WatchlistRecord:
    source: str
    source_url: str
    reference: str
    primary_name: str
    aliases: list[str]
    dates_of_birth: list[str]
    nationalities: list[str]
    record_type: str
    listed_on: str = ""


def _norm(value: str) -> str:
    return " ".join(re.sub(r"[^a-z0-9 ]", " ", value.casefold()).split())


def _texts(node: ElementTree.Element, tag: str) -> list[str]:
    values = []
    for item in node.iter():
        if item.tag.rsplit("}", 1)[-1] == tag and item.text and item.text.strip() and item.text.strip().lower() != "na":
            values.append(item.text.strip())
    return values


def _first(node: ElementTree.Element, tag: str) -> str:
    values = _texts(node, tag)
    return values[0] if values else ""


def parse_un_xml(content: bytes, source: str, source_url: str) -> list[WatchlistRecord]:
    root = ElementTree.fromstring(content)
    records: list[WatchlistRecord] = []
    if root.tag.rsplit("}", 1)[-1] == "NewDataSet":
        for node in root:
            values = {item.tag.rsplit("}", 1)[-1]: (item.text or "").strip() for item in node}
            primary = values.get("FullName") or values.get("FirstName")
            if not primary:
                continue
            alias_text = values.get("IndividualAlias") or values.get("EntityAlias") or ""
            records.append(WatchlistRecord(
                source=source, source_url=source_url,
                reference=values.get("ReferenceNumber", ""), primary_name=primary,
                aliases=[item.strip() for item in re.split(r"[;,]", alias_text) if item.strip()],
                dates_of_birth=[values["IndividualDateOfBirth"]] if values.get("IndividualDateOfBirth") else [],
                nationalities=[values["Nationality"]] if values.get("Nationality") else [],
                record_type="individual" if values.get("IndividualID") else "entity",
                listed_on=values.get("ListedOn", ""),
            ))
        if not records:
            raise ValueError("Official XML contained no sanctions records")
        return records
    for node in root.iter():
        kind = node.tag.rsplit("}", 1)[-1]
        if kind not in {"INDIVIDUAL", "ENTITY"}:
            continue
        if kind == "INDIVIDUAL":
            primary = " ".join(filter(None, (_first(node, key) for key in ("FIRST_NAME", "SECOND_NAME", "THIRD_NAME", "FOURTH_NAME"))))
        else:
            primary = _first(node, "FIRST_NAME") or _first(node, "NAME")
        aliases = _texts(node, "ALIAS_NAME")
        if not primary:
            continue
        records.append(WatchlistRecord(
            source=source,
            source_url=source_url,
            reference=_first(node, "REFERENCE_NUMBER") or _first(node, "DATAID"),
            primary_name=primary,
            aliases=aliases,
            dates_of_birth=_texts(node, "DATE") + _texts(node, "YEAR"),
            nationalities=_texts(node, "VALUE"),
            record_type=kind.lower(),
            listed_on=_first(node, "LISTED_ON"),
        ))
    if not records:
        raise ValueError("Official XML contained no sanctions records")
    return records


def _name_score(query: str, candidate: str) -> float:
    left, right = _norm(query), _norm(candidate)
    if not left or not right:
        return 0.0
    if left == right:
        return 1.0
    left_tokens, right_tokens = set(left.split()), set(right.split())
    overlap = len(left_tokens & right_tokens) / max(len(left_tokens), len(right_tokens))
    sequence = SequenceMatcher(None, left, right).ratio()
    return round(max(sequence, overlap * 0.92), 3)


def screen_official_sources(names: list[str], dob=None, nationality: str | None = None, threshold: float = 0.78) -> tuple[list[dict], dict]:
    queries = [name.strip() for name in names if name and name.strip()]
    coverage: dict = {}
    findings: list[dict] = []
    seen: set[tuple[str, str]] = set()
    tls_context = truststore.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    headers = {"User-Agent": "AML-Nexus-Enterprise/0.1 sanctions-screening local-development"}
    with httpx.Client(headers=headers, timeout=httpx.Timeout(25.0), follow_redirects=True, verify=tls_context) as client:
        for source, download_url, evidence_url in OFFICIAL_SOURCES:
            retrieved_at = datetime.now(timezone.utc).isoformat()
            try:
                response = client.get(download_url)
                response.raise_for_status()
                records = parse_un_xml(response.content, source, evidence_url)
                matches = 0
                for record in records:
                    candidates = [record.primary_name, *record.aliases]
                    best = max((( _name_score(query, candidate), query, candidate) for query in queries for candidate in candidates), default=(0.0, "", ""))
                    name_score, matched_query, matched_list_name = best
                    dob_match = bool(dob and any(str(dob) in value or str(dob.year) == value for value in record.dates_of_birth))
                    nationality_match = bool(nationality and any(_norm(nationality) in _norm(value) for value in record.nationalities))
                    score = min(1.0, name_score + (0.08 if dob_match else 0) + (0.04 if nationality_match else 0))
                    if score < threshold:
                        continue
                    key = (record.reference or record.primary_name, source)
                    if key in seen:
                        continue
                    seen.add(key); matches += 1
                    findings.append({
                        "title": record.primary_name,
                        "publication": source,
                        "url": evidence_url,
                        "excerpt": f"Official {record.record_type} record {record.reference or 'reference unavailable'}; matched '{matched_query}' to '{matched_list_name}'.",
                        "category": "sanctions_candidate",
                        "relevance": round(score, 3),
                        "match_factors": {"query": matched_query, "listed_name": matched_list_name, "name_score": name_score, "dob_match": dob_match, "nationality_match": nationality_match, "reference": record.reference, "listed_on": record.listed_on},
                    })
                coverage[source] = {"status": "success", "url": evidence_url, "download_url": download_url, "retrieved_at": retrieved_at, "records": len(records), "candidates": matches}
            except Exception as exc:
                coverage[source] = {"status": "failed", "url": evidence_url, "download_url": download_url, "retrieved_at": retrieved_at, "records": 0, "candidates": 0, "error": str(exc)[:300]}
    findings.sort(key=lambda item: item["relevance"], reverse=True)
    return findings, coverage
