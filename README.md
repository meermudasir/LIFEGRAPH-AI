<!--
  LIFEGRAPH AI — Project README
  Keep feature claims aligned with the current implementation.
-->

<div align="center">

# LIFEGRAPH AI

### Connected Intelligence · Graph Analytics · Vector Search

An AI-powered platform for exploring connected data, analysing graph relationships, and discovering semantic similarities.

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-API-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-ORM-D71F00?style=for-the-badge)](https://www.sqlalchemy.org/)
[![NetworkX](https://img.shields.io/badge/NetworkX-Graph%20Analysis-013243?style=for-the-badge)](https://networkx.org/)
[![License](https://img.shields.io/badge/License-Not%20specified-lightgrey?style=for-the-badge)](#)

**Explore relationships. Find patterns. Turn connected data into insight.**

</div>

---

## Overview

**LIFEGRAPH AI** is a connected-intelligence application built around graph analytics and vector-based similarity. It combines a Python API with graph and text-processing components to help users explore entities, relationships, and related information through a unified platform.

The repository includes a browser-based interface, a FastAPI backend, database models, graph and vector services, and account authentication pages.

> Project status: actively developed. Features and deployment configuration may evolve.

## Core capabilities

| Area | What it provides |
|---|---|
| Graph analytics | Model and explore entities and their relationships using NetworkX |
| Vector similarity | TF-IDF-based text vectorisation and similarity search |
| API layer | FastAPI endpoints for dashboard, graph, vector, query, intelligence, analytics, and authentication workflows |
| Data persistence | SQLAlchemy models with SQLite configured by default for local development; PostgreSQL driver included |
| Account access | Email/password registration and login, signed session tokens, and HttpOnly session cookies |
| Google OAuth | OAuth integration code and environment-variable configuration |
| Sample data | Startup routine can seed the sample dataset when the database is empty |

## Technology stack

- **Backend:** Python, FastAPI, Uvicorn
- **Data and persistence:** SQLAlchemy, SQLite (default), PostgreSQL driver
- **Graph processing:** NetworkX
- **Vector / machine-learning utilities:** NumPy, scikit-learn (TF-IDF)
- **Authentication:** bcrypt, PyJWT, Google OAuth integration
- **Frontend:** HTML, CSS, JavaScript
- **Testing:** pytest

## Repository layout

```text
LIFEGRAPH-AI/
├── backend/
│   ├── api/             # FastAPI route modules
│   ├── core/            # Security, OAuth, graph and vector engines
│   ├── data/            # Sample data
│   ├── services/        # Application services
│   ├── config.py        # Environment-based settings
│   ├── database.py      # SQLAlchemy engine and sessions
│   ├── models.py        # Database models
│   ├── schemas.py       # Request and response schemas
│   └── main.py          # FastAPI application entry point
├── tests/               # API and security tests
├── index.html           # Main application interface
├── login.html           # Login page
├── signup.html          # Registration page
├── style.css            # Application styles
├── script.js            # Main frontend logic
├── auth.js              # Frontend authentication controller
├── requirements.txt     # Python dependencies
└── .env.example         # Environment configuration template
```

## Getting started

### 1. Clone the repository

```bash
git clone https://github.com/meermudasir/LIFEGRAPH-AI.git
cd LIFEGRAPH-AI
```

### 2. Create and activate a virtual environment

**Windows PowerShell**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**macOS / Linux**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configure environment variables

Copy the example file:

```powershell
Copy-Item .env.example .env
```

For local development, the example uses SQLite. Review `.env` and set values appropriate to your environment.

**Important:** Never commit `.env`, production credentials, OAuth secrets, or real user data. Use a strong, unique `SECRET_KEY` and production-specific CORS origins when deploying.

Google OAuth requires credentials from a Google Cloud project and the corresponding authorised redirect URI configuration. Leave the Google credential values empty when you are not configuring Google sign-in.

### 5. Start the API

```bash
uvicorn backend.main:app --reload
```

The API is available locally at:

- API root: http://127.0.0.1:8000/
- Health check: http://127.0.0.1:8000/health
- Interactive API docs: http://127.0.0.1:8000/docs
- Alternative API docs: http://127.0.0.1:8000/redoc

### 6. Open the frontend

Serve the repository's HTML files with a local static development server (for example, the VS Code Live Server extension). Open `index.html`, `login.html`, or `signup.html` from that server.

The frontend must be configured to send API requests to the backend origin. For local development, the authentication controller falls back to port `8000`; for a hosted environment, configure the frontend API base URL to the deployed backend URL and ensure the backend CORS allowlist includes the frontend origin.

## Running tests

Run the test suite from the repository root:

```bash
python -m pytest -q
```

## Configuration reference

The main settings are documented in `.env.example`, including:

- `DATABASE_URL` — database connection string
- `SECRET_KEY` — signing key for application sessions
- `ENVIRONMENT` and `DEBUG` — runtime mode
- `CORS_ORIGINS` — comma-separated allowed frontend origins
- `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` — optional Google OAuth credentials
- `VECTOR_MAX_FEATURES`, `DEFAULT_SIMILARITY_THRESHOLD`, and `DEFAULT_TOP_K` — vector search settings

For production, use a managed persistent database, configure all secrets through the hosting provider's environment settings, use HTTPS, and set the exact frontend origin in `CORS_ORIGINS`. Do not rely on an ephemeral local SQLite file for production user accounts.

## API route groups

The backend registers route groups for:

- Authentication
- Dashboard
- Graph operations
- Vector operations
- Query operations
- Intelligence
- Analytics

The API documentation at `/docs` is the source of truth for the currently exposed endpoints and request schemas.

## Security notes

- Passwords are stored as password hashes, not as plain text.
- Session tokens are signed and delivered using an HttpOnly cookie.
- Production startup validates that a non-default secret key of sufficient length is configured.
- Configure secure cookies, HTTPS, CORS, database access, and OAuth redirect URLs for the actual production domains before enabling public sign-ups.

This documentation does not constitute a production security certification. Review deployment settings and test authentication flows in the target environment before inviting real users.

## Contributing

Issues and pull requests are welcome. When proposing a change:

1. Describe the problem and intended behaviour.
2. Keep secrets and personal data out of commits and issue reports.
3. Add or update tests for changed behaviour.
4. Run the test suite before submitting a pull request.

## Maintainer

**Mudasir Reyaz**  
GitHub: [@meermudasir](https://github.com/meermudasir)

---

<div align="center">

**LIFEGRAPH AI** · Building connected intelligence.

</div>
