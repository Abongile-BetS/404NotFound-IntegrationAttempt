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

5. Backend Setup
Navigate to the backend directory:

cd backend

Create a Python virtual environment: python -m venv .venv

Activate the virtual environment.
Windows
.venv\Scripts\activate

Install the backend dependencies: pip install -r requirements.txt

Start the FastAPI development server: uvicorn app.main:app --reload

The backend should now be available at: http://localhost:8000
FastAPI API documentation is available at: http://localhost:8000/docs

6. Frontend Setup
Open a new terminal and navigate to the frontend directory:

cd frontend

Install the frontend dependencies:
npm install (Make sure you have Node.js installed before, verify using [node --version] command)

Start the development server:

npm run dev

The frontend will be available at the URL displayed by the development server.

7. Running the Complete Application
For local development, the recommended startup sequence is:

Terminal 1 — Infrastructure
From the project root:

docker compose up -d

Terminal 2 — Backend
cd backend

python -m venv .venv

source .venv/bin/activate

pip install -r requirements.txt

uvicorn app.main:app --reload

Terminal 3 — Frontend
cd frontend

npm install

npm run dev

The application should now be running with:

Frontend
   │
   ├── Authentication ──► Keycloak
   │
   └── API Requests ────► FastAPI Backend
                              │
                              ├── Application Database
                              │
                              └── Neo4j

# 404NotFound-IntegrationAttempt
