# 404NotFound

# AI-Powered AML/KYC Risk Intelligence Platform

## Overview

The AML/KYC Risk Intelligence Platform is a centralized compliance solution designed for online gambling institutions.

The platform combines customer, KYC, transaction, betting, device, and relationship data to generate explainable risk scores, identify potentially suspicious activity, reduce false positives, prioritize alerts, and support AML investigations.

This platform is designed to augment compliance teams by providing risk intelligence and investigation support rather than replacing human decision-making.

## Vision

Transform high-frequency gambling activity data into actionable risk intelligence that enables compliance teams to:

- Identify high-risk customers
- Understand why customers are considered high-risk
- Prioritize investigations
- Reduce false positives
- Visualize customer relationships
- Improve AML/KYC compliance
- Improve operational efficiency

## Key Capabilities

### Customer Management

- Customer profiles
- Customer risk classification
- Source of Funds
- Source of Wealth

### KYC Monitoring

- Verification status tracking
- Review workflows
- Compliance monitoring

### PEP & Sanctions Screening

- PEP screening
- Sanctions screening
- Screening result management

### Transaction Monitoring

- Deposits
- Withdrawals
- Betting activity
- Behavioural monitoring

### Risk Scoring

- Explainable risk scores
- Risk factors
- Risk history
- Risk prioritization

### Alert Management

- Alert generation
- Severity classification
- Workflow tracking

### Investigation Management

- Investigations
- Notes
- Case outcomes
- False positive tracking

### Graph Intelligence

- Customer relationships
- Shared devices
- Shared payment methods
- Neo4j graph visualization

### Reporting

- Risk dashboards
- Alert dashboards
- Investigation dashboards
- Compliance reporting


# Architecture

The platform follows:

- Domain Driven Design (DDD)
- Clean Architecture
- Modular Monolith Architecture

The MVP is intentionally designed as a modular monolith to support rapid delivery, maintainability, and future scalability.

## Run locally

The application source is in `aml-risk-platform`.

### Quick start (recommended for non-technical users)

Double-click `aml-risk-platform/start.bat`. It will:

1. Install backend and frontend dependencies.
2. Create `backend/.env` and `frontend/.env` if needed.
3. Enable local development auth bypass when Keycloak is not detected.
4. Load demo seed data.
5. Start the backend and frontend.
6. Open `http://localhost:5173` in your browser.

### Manual start

Prerequisites: Python 3.12+ and Node.js 24+. PostgreSQL and Keycloak are
optional because the app can use an embedded PostgreSQL instance and a
development auth bypass.

```powershell
Set-Location .\aml-risk-platform
.\scripts\setup-local.ps1
.\scripts\run-local.ps1
```

Optional seed data:

```powershell
Set-Location .\aml-risk-platform\backend
python seed.py
```

### Run tests

Backend:

```powershell
Set-Location .\aml-risk-platform\backend
python -m unittest discover -s app\tests
```

Frontend:

```powershell
Set-Location .\aml-risk-platform\frontend
npm test
npm run lint
npm run build
```

### URLs

- Frontend: `http://localhost:5173`
- Backend docs: `http://localhost:8000/docs`
- Health: `http://localhost:8000/health`

PostgreSQL and Keycloak are optional for local development. For production-like
configuration, set real credentials in `backend/.env` and disable
`DEV_AUTH_BYPASS`.

See [aml-risk-platform/INTEGRATION_README.md](./aml-risk-platform/INTEGRATION_README.md)
for integration details.

# 404NotFound-IntegrationAttempt
