# ACEest Fitness and Gym DevOps

Flask API converted from ACEest Tkinter versions with SQLite persistence, CI/CD automation, and test coverage.

## Overview

This API supports:

1. User login (`admin/admin` default user)
2. Program catalog
3. Client management with calorie calculation
4. Membership management
5. Weekly progress tracking
6. Workout logging
7. Metrics and BMI insights
8. AI-style workout plan generation

## Endpoints

1. `POST /auth/login`
2. `GET /`
3. `GET /programs`
4. `GET /programs/<slug>`
5. `GET /clients`
6. `POST /clients`
7. `GET /clients/<name>`
8. `GET /clients/<name>/membership`
9. `PATCH /clients/<name>/membership`
10. `GET /clients/<name>/summary`
11. `GET /clients/<name>/bmi`
12. `GET /clients/export`
13. `POST /progress`
14. `GET /progress/<name>`
15. `GET /progress/<name>/chart`
16. `POST /workouts`
17. `GET /workouts/<name>`
18. `POST /metrics`
19. `GET /metrics/<name>`
20. `GET /metrics/<name>/weight-chart`
21. `POST /ai-program`

## Membership Field Compatibility

The API supports both field names from different Tkinter versions:

1. `membership_expiry` (canonical API field)
2. `membership_end` (alias for compatibility)

You can send either in create/update payloads. Responses include both fields for convenience.

## Local Setup

```bash
python -m venv .venv
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt
python app.py
```

Run tests:

```bash
python -m pytest -q
```

## Sample Requests

### Login

```json
{
  "username": "admin",
  "password": "admin"
}
```

### Create Client

```json
{
  "name": "Asha",
  "age": 28,
  "height": 165,
  "weight": 60,
  "program": "Fat Loss (FL) - 3 day",
  "target_weight": 56,
  "target_adherence": 85,
  "membership_status": "Active",
  "membership_end": "2026-12-31"
}
```

### Update Membership

```json
{
  "membership_status": "Expired",
  "membership_expiry": "2025-12-31"
}
```

### AI Program

```json
{
  "client_name": "Asha",
  "experience": "intermediate"
}
```

## Tech Stack

1. Python 3
2. Flask
3. SQLite3
4. Pytest
5. Docker and Docker Compose
6. GitHub Actions
7. Jenkins
