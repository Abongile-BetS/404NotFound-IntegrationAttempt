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

The application source is in `aml-risk-platform`. Install PostgreSQL, Keycloak,
Python 3.12+, and Node.js 24+ locally. Follow
[the local setup guide](./aml-risk-platform/docs/LOCAL_SETUP.md) to configure
the database, authentication realm, and environment.

From PowerShell, follow the local setup guide or run its setup helper:

```powershell
Set-Location .\aml-risk-platform
.\scripts\setup-local.ps1
```

Edit `.env` with your local PostgreSQL credentials, start PostgreSQL, deploy
the schema, and start Keycloak as described in the guide. Then run:

```powershell
.\scripts\run-local.ps1
```

The frontend is at `http://localhost:5173`, backend docs at
`http://localhost:8000/docs`, and local Keycloak at `http://localhost:8080`.
PostgreSQL and Keycloak must be installed and running outside the application;
this repository no longer includes Docker configuration.

See [aml-risk-platform/INTEGRATION_README.md](./aml-risk-platform/INTEGRATION_README.md)
for integration details.

# 404NotFound-IntegrationAttempt
