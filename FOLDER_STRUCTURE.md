# DavnorShield API - Folder Structure Documentation

This document provides a comprehensive overview of the DavnorShield API project structure, detailing the purpose and functions of each folder and its components.

## Project Overview

**DavnorShield API** is an AI-powered community cyber threat intelligence platform for Davao del Norte. It provides threat detection, analysis, and community-wide cybersecurity awareness through various intelligent systems and geospatial analytics.

---

## Root-Level Files

| File | Purpose |
|------|---------|
| `main.py` | FastAPI application entry point; initializes the app, middleware, routers, and lifecycle management |
| `config.py` | Environment configuration and settings management |
| `constants.py` | Application-wide constants and static values |
| `requirements.txt` | Python package dependencies |
| `.env.example` | Example environment variables template |
| `alembic.ini` | Alembic database migration configuration |
| `Dockerfile` | Docker container specification for deployment |
| `docker-compose.yml` | Multi-container deployment configuration |

---

## Core Application Structure (`app/`)

### 📡 **api/** - REST API Endpoints

Houses all FastAPI route handlers organized by API version.

#### **api/v1/** - Version 1 API Endpoints

**Main Router** (`router.py`):
- Aggregates all v1 endpoints
- Includes tags for API documentation organization

**Endpoint Modules**:

| Module | Endpoints | Functions |
|--------|-----------|-----------|
| `auth.py` | `/auth/*` | User registration, login, token refresh, session management |
| `users.py` | `/users/*` | User management, admin operations, user role assignments |
| `reports.py` | `/reports/*` | Submit and retrieve scam/threat reports, report validation |
| `scanner.py` | `/scanner/*` | Threat scanning, URL/email analysis, phishing detection |
| `alerts.py` | `/alerts/*` | Broadcast alerts, locality-specific alerts, push notifications |
| `weather.py` | `/weather/*` | Cyber weather forecasting, risk level predictions |
| `heatmap.py` | `/heatmap/*` | Geospatial scam/threat clustering, hotspot identification |
| `barangays.py` | `/barangays/*` | Barangay reference data, statistics, locality reports |
| `municipalities.py` | `/municipalities/*` | Municipality data, summaries, regional analytics |
| `dashboard.py` | `/dashboard/*` | LGU dashboards, administrative analytics, performance metrics |
| `schools.py` | `/schools/*` | School awareness programs, phishing statistics, educational data |

---

### 🤖 **ai/** - Artificial Intelligence Engines

Contains specialized AI modules for threat detection, pattern analysis, and risk assessment.

| Module | Purpose | Key Functions |
|--------|---------|---|
| `classifier.py` | Threat classification | Categorizes threats into types (phishing, scam, SMS fraud, etc.) |
| `phishing_detector.py` | Phishing detection | Analyzes URLs and emails for phishing indicators |
| `sms_detector.py` | SMS threat detection | Identifies suspicious SMS messages and patterns |
| `qr_detector.py` | QR code analysis | Scans QR codes for malicious links or payloads |
| `keyword_model.py` | Keyword extraction | Extracts and analyzes suspicious keywords from reports |
| `pattern_engine.py` | Pattern recognition | Detects patterns in threat data across geographies |
| `cyber_weather_engine.py` | Risk forecasting | Predicts daily cyber risk levels and threat weather |
| `outbreak_detector.py` | Outbreak detection | Identifies sudden increases in threat reports (outbreaks) |
| `reputation_engine.py` | Reputation scoring | Assigns risk scores to domains, IPs, and entities |
| `recommendation_engine.py` | Recommendations | Suggests mitigation strategies and alerts to users |
| `key_model.py` | Key model utilities | Placeholder for future key threat model components |

---

### 🔐 **core/** - Core Application Logic

Handles authentication, authorization, security, and Firebase integration.

| Module | Purpose | Functions |
|--------|---------|-----------|
| `auth.py` | Authentication logic | JWT token validation, user credential verification |
| `security.py` | Security utilities | Password hashing (bcrypt), token generation, encryption |
| `permissions.py` | Authorization | Role-based access control (RBAC), permission checking |
| `firebase.py` | Firebase integration | FCM push notifications, Firebase Realtime Database operations |

---

### 💾 **database/** - Database Configuration & Initialization

Manages database connections, sessions, and initialization.

| Module | Purpose | Functions |
|--------|---------|-----------|
| `base.py` | Base configuration | SQLAlchemy declarative base, ORM foundation |
| `session.py` | Database sessions | Session factory, connection pooling configuration |
| `init_db.py` | Database initialization | Creates tables, runs migrations, initializes seed data |

---

### 📊 **models/** - SQLAlchemy ORM Models

Defines the database schema and entity relationships.

**Common Models**:
- **User**: User accounts, roles, authentication
- **Report**: Scam/threat reports with geospatial data
- **Alert**: System alerts and notifications
- **Threat**: Detected threats and classifications
- **Weather**: Cyber weather predictions
- **Barangay/Municipality**: Geographic reference entities
- **School**: School data and metrics
- **Notification**: Push notification records

---

### 📋 **schemas/** - Pydantic Request/Response Schemas

Defines data validation and serialization for API requests/responses.

**Schema Types**:
- **Request Schemas**: Data validation for incoming API requests
- **Response Schemas**: Serialization for outgoing API responses
- **Base Schemas**: Common fields and mixins

---

### 🛠️ **services/** - Business Logic Layer

Implements business rules, orchestrates repositories, and handles complex operations.

| Module | Purpose | Key Operations |
|--------|---------|---|
| `auth_service.py` | Authentication logic | Login, registration, token management, password verification |
| `user_service.py` | User management | CRUD operations, role assignments, user queries |
| `report_service.py` | Report processing | Validate, classify, analyze submitted reports |
| `scanner_service.py` | Threat scanning | Scan URLs/emails, integrate AI detectors, return threat scores |
| `alert_service.py` | Alert management | Create, broadcast, and track alerts across localities |
| `weather_service.py` | Cyber weather | Generate daily forecasts, risk predictions |
| `heatmap_service.py` | Geospatial analysis | Cluster threats, identify hotspots, geographic stats |
| `barangay_service.py` | Barangay operations | Retrieve data, generate statistics, community metrics |
| `municipality_service.py` | Municipality operations | Regional summaries, LGU-level analytics |
| `dashboard_service.py` | Dashboard data | Compile metrics, KPIs, and insights for LGU dashboards |
| `school_service.py` | School programs | Manage awareness programs, track statistics |
| `notification_service.py` | Notifications | Push notifications, user message delivery |
| `outbreak_service.py` | Outbreak detection | Analyze clusters, detect sudden spikes |
| `pattern_service.py` | Pattern analysis | Extract patterns, generate insights |
| `audit_service.py` | Audit logging | Track actions, maintain audit trail |

---

### 💾 **repositories/** - Data Access Layer

Implements database queries and CRUD operations. Follows the Repository Pattern.

| Module | Purpose | Operations |
|--------|---------|-----------|
| `base.py` | Base repository | Common CRUD methods, query utilities |
| `user_repository.py` | User queries | Get users, create users, update profiles |
| `report_repository.py` | Report queries | Complex report queries, filtering, geospatial searches |
| `alert_repository.py` | Alert queries | Alert retrieval, status updates, broadcast tracking |
| `threat_repository.py` | Threat queries | Threat analysis, categorization queries |
| `weather_repository.py` | Weather queries | Forecast storage and retrieval |
| `heatmap_repository.py` | Heatmap queries | Geospatial clustering, hotspot data |
| `barangay_repository.py` | Barangay queries | Reference data retrieval |
| `municipality_repository.py` | Municipality queries | Regional data queries |
| `school_repository.py` | School queries | School data and statistics |
| `notification_repository.py` | Notification queries | Delivery tracking, user preferences |
| `audit_repository.py` | Audit log queries | Retrieve audit trails, compliance reports |

---

### 🔧 **utils/** - Utility Functions

Provides helper functions and utilities used across the application.

**Common Utilities**:
- **String/Data Processing**: Text sanitization, data formatting
- **Date/Time Helpers**: Timestamp utilities, timezone conversion
- **Geospatial Helpers**: Coordinate calculations, distance measurements
- **Validation Helpers**: Email, phone, URL validation
- **Error Handling**: Custom exception classes

---

### ⚙️ **workers/** - Background Jobs & Scheduling

Manages asynchronous tasks, scheduled jobs, and background processes.

**Common Workers**:
- **scheduler.py**: APScheduler configuration and job scheduling
- **Periodic Tasks**: 
  - Daily cyber weather predictions
  - Outbreak detection checks
  - Notification batch processing
  - Report aggregation
  - Cache updates

---

## Supporting Directories

### **alembic/** - Database Migrations

Handles database schema versioning and migrations using Alembic.

| File | Purpose |
|------|---------|
| `env.py` | Alembic environment configuration |
| `versions/` | Migration scripts (one per schema change) |

---

## Architecture Flow

```
Client (Flutter/Web)
    ↓
FastAPI Router (api/v1/)
    ↓
Services (services/)
    ↓
Repositories (repositories/)
    ↓
SQLAlchemy Models (models/)
    ↓
PostgreSQL Database
    ↑
AI Engines (ai/) ← Reports & Data Analysis
    ↑
Workers (workers/) ← Scheduled Tasks & Notifications
```

---

## Key Design Patterns

### Layered Architecture
1. **API Layer** (`api/v1/`): HTTP endpoints
2. **Service Layer** (`services/`): Business logic
3. **Repository Layer** (`repositories/`): Data access
4. **Model Layer** (`models/`): Database schema
5. **AI/Utility Layers** (`ai/`, `utils/`): Specialized operations

### Repository Pattern
- Abstracts data access
- Enables testability
- Centralizes database queries

### Service Layer Pattern
- Encapsulates business logic
- Orchestrates repositories
- Handles complex operations

---

## Development Workflow

### Adding a New Feature

1. **Create Database Model** (`models/new_model.py`)
2. **Create Alembic Migration** (`alembic/versions/`)
3. **Create Repository** (`repositories/new_repository.py`)
4. **Create Service** (`services/new_service.py`)
5. **Create Schemas** (`schemas/new_schema.py`)
6. **Create API Endpoints** (`api/v1/new_endpoint.py`)
7. **Add to Router** (`api/v1/router.py`)

### Database Changes

```bash
# Create migration
alembic revision --autogenerate -m "description"

# Apply migration
alembic upgrade head
```

### Running the Application

```bash
# Development (with auto-reload)
uvicorn app.main:app --reload

# Production
gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app
```

---

## Dependencies Overview

### Core
- **FastAPI**: Web framework
- **SQLAlchemy**: ORM
- **Pydantic**: Data validation
- **Alembic**: Database migrations

### Authentication & Security
- **python-jose**: JWT token handling
- **passlib[bcrypt]**: Password hashing
- **firebase-admin**: Firebase services

### Data & AI
- **pandas**: Data manipulation
- **numpy**: Numerical operations
- **scikit-learn**: ML utilities

### Background Tasks
- **APScheduler**: Task scheduling

### Database
- **psycopg2**: PostgreSQL adapter

---

## Environment Variables

Required `.env` variables:

```
DATABASE_URL=postgresql://user:password@localhost/davnorshield
SECRET_KEY=your_secret_key_here
FIREBASE_PROJECT_ID=your_firebase_project
FIREBASE_CREDENTIALS_PATH=./firebase-credentials.json
ALLOWED_ORIGINS=http://localhost:3000,https://example.com
UPLOAD_DIR=./uploads
```

---

## Testing & Quality

- **Unit Tests**: Test individual functions/services
- **Integration Tests**: Test API endpoints and services together
- **AI Model Tests**: Validate threat detection accuracy
- **Database Tests**: Test repository operations

---

## Deployment

### Docker Deployment
```bash
docker compose up --build
```

### Environment
- Production database: PostgreSQL 17+
- Container orchestration: Docker/Docker Compose
- Reverse proxy: Nginx (recommended)

---

## Summary

DavnorShield API follows a clean, layered architecture that separates concerns into API handlers, business logic, data access, and AI/utility functions. This design enables scalability, testability, and maintainability while providing a comprehensive cyber threat intelligence platform for the Davao del Norte community.

