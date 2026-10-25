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

## Run locally with Docker

The runnable application and its Compose file are in `aml-risk-platform`. From PowerShell:

```powershell
Set-Location .\aml-risk-platform
Copy-Item .env.example .env
```

Edit `.env` and replace all three password placeholders. Use URL-safe characters for `POSTGRES_PASSWORD`. With Docker Desktop running, validate and start the stack:

```powershell
docker compose config --quiet
docker compose up --build -d
```

This starts PostgreSQL, Keycloak, the FastAPI backend and the frontend. Open:

- Frontend: `http://localhost:5173`
- Backend API docs: `http://localhost:8000/docs`
- Keycloak: `http://localhost:8080`

The database schema is deployed automatically only when PostgreSQL creates a new data volume. To stop the stack without deleting data, run `docker compose down`. The optional demo ETL job can be run after startup with `docker compose --profile etl run --rm etl-engine`.

See [aml-risk-platform/INTEGRATION_README.md](./aml-risk-platform/INTEGRATION_README.md) for integration details and [aml-risk-platform/docs/CONSOLIDATION_AND_DOCKER.md](./aml-risk-platform/docs/CONSOLIDATION_AND_DOCKER.md) for deployment limitations. Docker is not installed in every development environment, so the Compose stack must be built and run on a machine with Docker Desktop.

# 404NotFound-IntegrationAttempt
