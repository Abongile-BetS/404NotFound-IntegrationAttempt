# AML rules

The additive on-demand evaluator contains 12 deterministic checks in `backend/app/modules/enterprise_extension/engine.py`. They run against available customer financial transactions, KYC fields, recorded screening results, country data and shared-device links.

| Code | Check | Default trigger |
|---|---|---|
| AML-TXN-001 | Seven-day withdrawal/deposit ratio | 7d deposit and withdrawal are each at least R10,000; withdrawals/deposits >= 0.8 |
| AML-TXN-002 | Deposit activity spike | Prior 30d deposits >= R1,000 and current 30d growth >= 150% |
| AML-TXN-003 | High deposit frequency | At least 10 deposits in 7d |
| AML-TXN-004 | Unusual withdrawal frequency | At least 8 withdrawals in 7d |
| AML-BHV-001 | Dormant-to-active behaviour | Prior deposit >= 60 days ago and current 30d deposits >= R10,000 |
| AML-BHV-002 | Large average deposit | Average 30d deposit >= R10,000 |
| AML-KYC-001 | CDD incomplete | FICA-compliant field is explicitly false |
| AML-SCR-001 | Potential sanctions hit | A recorded sanctions screening is a match or review candidate |
| AML-SCR-002 | Potential PEP hit | A recorded PEP screening is a match or review candidate |
| AML-MED-001 | Potential adverse media | A recorded media screening is a match or review candidate |
| AML-NET-001 | Shared-device relationships | At least two other customers share a recorded device |
| AML-GEO-001 | Geographic profile missing | Customer country is blank |

Thresholds and point weights currently come from the extension's code constants. The separate 404NotFound `risk.rules` / `rule_parameter` / `rule_version` catalogue is displayed by the existing rule view but does not currently configure this extension's evaluator. Rule administration, approval and version activation are not implemented here.

All checks return `TRIGGERED`, `CLEAR` or `UNAVAILABLE`; a clear result requires the relevant source to have data. Network links are computed from the PostgreSQL customer-device relationship table. The seven-day withdrawal/deposit ratio is not time-sequenced rapid-movement detection. No PEP, sanctions or adverse-media source is queried live. Screening candidates are not confirmed identity matches.

The evaluator is read-only and on-demand. It does not replace the host risk score, write `risk.rule_result`, persist its own assessments, create alerts/cases, or run automatically when customer or transaction data changes. Scores and thresholds are illustrative and require formal compliance approval before operational use.
